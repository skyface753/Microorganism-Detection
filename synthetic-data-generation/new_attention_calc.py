import cv2
import numpy as np
import csv
from ultralytics import YOLO
from yolo_cam.eigen_cam import EigenCAM
from yolo_cam.utils.image import show_cam_on_image
from PIL import Image
import os
import warnings
import argparse

warnings.filterwarnings("ignore")

# Metrics functions
def compute_box_coverage(cam: np.ndarray, boxes: list, threshold_ratio=0.3) -> float:
    cam_norm = cam.astype(np.float32)
    cam_norm /= cam_norm.max() + 1e-8
    total_mass = cam_norm.sum()
    in_box = sum(cam_norm[int(y1):int(y2), int(x1):int(x2)].sum() for x1,y1,x2,y2 in boxes)
    return in_box / (total_mass + 1e-8)

def compute_center_distance(cam: np.ndarray, boxes: list) -> float:
    H, W = cam.shape
    ys, xs = np.indices((H, W))
    mass = cam.astype(np.float32)
    total = mass.sum() + 1e-8
    com_x = (xs * mass).sum() / total
    com_y = (ys * mass).sum() / total
    dists = []
    for x1, y1, x2, y2 in boxes:
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        dist = np.hypot(com_x - cx, com_y - cy)
        norm = np.hypot(x2 - x1, y2 - y1)
        dists.append(dist / (norm + 1e-8))
    return float(np.mean(dists))

def load_yolo_labels(images_dir: str, labels_dir: str, size=(800,600)) -> dict:
    annots = {}
    for fn in os.listdir(images_dir):
        base, ext = os.path.splitext(fn)
        if ext.lower() not in ['.jpg', '.png', '.jpeg']:
            continue
        img = cv2.imread(os.path.join(images_dir, fn))
        h0, w0 = img.shape[:2]
        sx, sy = size[0] / w0, size[1] / h0
        boxes = []
        lp = os.path.join(labels_dir, base + '.txt')
        if os.path.exists(lp):
            for line in open(lp):
                parts = line.split()
                if len(parts) != 5:
                    continue
                _, xc, yc, w, h = map(float, parts)
                xc, yc = xc * w0, yc * h0
                w, h = w * w0, h * h0
                x1, y1 = xc - w/2, yc - h/2
                x2, y2 = xc + w/2, yc + h/2
                boxes.append([x1 * sx, y1 * sy, x2 * sx, y2 * sy])
        annots[fn] = boxes
    return annots

def process_single_image(model, img_path: str, layer, boxes, exp: str, layer_idx: int, metrics):
    img = cv2.imread(img_path)
    resized = cv2.resize(img, (800, 600))
    inp = resized.astype(np.float32) / 255
    cam_extractor = EigenCAM(model, [layer], task='od')
    cam_map = cam_extractor(resized)[0]
    cov = compute_box_coverage(cam_map, boxes)
    dist = compute_center_distance(cam_map, boxes)
    metrics[exp].append({'layer': layer_idx, 'coverage': cov, 'dist': dist})

    cam_img = show_cam_on_image(inp, cam_map, use_rgb=True)
    for x1, y1, x2, y2 in model(resized)[0].boxes.xyxy:
        cv2.rectangle(cam_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
    out_dir = f"cam_{exp}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{os.path.basename(img_path)}_l{layer_idx}.jpg")
    cv2.imwrite(out_path, cam_img)


def doMultiScale(models, imgs, lbls, layers, dev):
    # Parse models: allow 'path:name' or 'path'
    mlist = []
    for m in models:
        if ':' in m:
            path, name = m.split(':', 1)
        else:
            path = m
            name = os.path.splitext(os.path.basename(path))[0]
        mlist.append((path, name))

    metrics = {name: [] for _, name in mlist}
    annotations = load_yolo_labels(imgs, lbls)

    for path, name in mlist:
        model = YOLO(path).to(dev)
        for fn, boxes in annotations.items():
            img_path = os.path.join(imgs, fn)
            for idx in layers:
                layer = model.model.model[idx]
                process_single_image(model, img_path, layer, boxes, name, idx, metrics)

    # Print summary and write CSV
    print("\nAttention Metrics Summary:")
    print("Exp | Layer | MeanCov | MeanDist | N")
    rows = []
    for exp, vals in metrics.items():
        if not vals:
            continue
        covs = [v['coverage'] for v in vals]
        dists = [v['dist'] for v in vals]
        print(f"{exp}|all|{np.mean(covs):.3f}|{np.mean(dists):.3f}|{len(vals)}")
        for v in sorted(vals, key=lambda x: x['layer']):
            print(f"{exp}|{v['layer']}|{v['coverage']:.3f}|{v['dist']:.3f}")
        # add the mean row
        rows.append({
            'experiment': exp,
            'layer': 'all',
            'coverage': np.mean(covs),
            'center_dist': np.mean(dists)
        })
        # flatten for CSV
        for v in vals:
            rows.append({
                'experiment': exp,
                'layer': v['layer'],
                'coverage': v['coverage'],
                'center_dist': v['dist']
            })

    csv_path = 'attention_metrics.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['experiment', 'layer', 'coverage', 'center_dist'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved metrics CSV to {csv_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', nargs='+', required=True)
    parser.add_argument('--images', required=True)
    parser.add_argument('--labels', required=True)
    parser.add_argument('--layers', nargs='+', type=int, default=[5,8,16,19,22])
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()
    doMultiScale(args.models, args.images, args.labels, args.layers, args.device)
