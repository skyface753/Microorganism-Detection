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
from collections import defaultdict # To easily manage metrics

warnings.filterwarnings("ignore")

# Metrics functions
def compute_box_coverage(cam: np.ndarray, boxes: list) -> float:
    """
    Computes the proportion of CAM mass that falls within the ground truth bounding boxes.
    """
    if not boxes: # Handle cases where there are no ground truth boxes
        return 0.0
    
    cam_norm = cam.astype(np.float32)
    # Normalize CAM to sum to 1 for meaningful proportion
    cam_norm /= (cam_norm.sum() + 1e-8)
    
    in_box_mass = 0.0
    for x1, y1, x2, y2 in boxes:
        # Ensure coordinates are within image bounds
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(cam_norm.shape[1], int(x2)), min(cam_norm.shape[0], int(y2))
        
        if x2 > x1 and y2 > y1: # Ensure valid box
            in_box_mass += cam_norm[y1:y2, x1:x2].sum()
            
    return in_box_mass

def compute_center_distance(cam: np.ndarray, boxes: list) -> float:
    """
    Computes the average normalized Euclidean distance between the center of mass
    of the CAM and the center of each ground truth bounding box.
    """
    if not boxes: # Handle cases where there are no ground truth boxes
        return 0.0
        
    H, W = cam.shape
    ys, xs = np.indices((H, W))
    
    mass = cam.astype(np.float32)
    total_mass = mass.sum() + 1e-8
    
    # Compute center of mass of the CAM
    com_x = (xs * mass).sum() / total_mass
    com_y = (ys * mass).sum() / total_mass
    
    dists = []
    for x1, y1, x2, y2 in boxes:
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        
        # Calculate Euclidean distance
        dist = np.hypot(com_x - cx, com_y - cy)
        
        # Normalize by the diagonal length of the bounding box
        # This makes the distance scale-invariant
        box_diagonal = np.hypot(x2 - x1, y2 - y1)
        if box_diagonal > 1e-8: # Avoid division by zero
            dists.append(dist / box_diagonal)
        else: # Handle tiny or invalid boxes gracefully
            dists.append(0.0)
            
    return float(np.mean(dists)) if dists else 0.0

def load_yolo_labels(images_dir: str, labels_dir: str, target_size=(800,600)) -> dict:
    """
    Loads YOLO format labels and converts them to pixel coordinates relative to target_size.
    """
    annots = {}
    for fn in os.listdir(images_dir):
        base, ext = os.path.splitext(fn)
        if ext.lower() not in ['.jpg', '.png', '.jpeg']:
            continue
        
        img_path = os.path.join(images_dir, fn)
        # Use PIL for robust image loading to get original size
        with Image.open(img_path) as img_pil:
            w0, h0 = img_pil.size
        
        sx, sy = target_size[0] / w0, target_size[1] / h0 # Scaling factors for resizing

        boxes = []
        lp = os.path.join(labels_dir, base + '.txt')
        if os.path.exists(lp):
            with open(lp, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        continue
                    _, xc_norm, yc_norm, w_norm, h_norm = map(float, parts)
                    
                    # Convert normalized YOLO format to pixel coordinates in original image
                    xc, yc = xc_norm * w0, yc_norm * h0
                    w, h = w_norm * w0, h_norm * h0
                    
                    x1, y1 = xc - w/2, yc - h/2
                    x2, y2 = xc + w/2, yc + h/2
                    
                    # Scale coordinates to the target_size for consistency with CAM
                    boxes.append([x1 * sx, y1 * sy, x2 * sx, y2 * sy])
        annots[fn] = boxes
    return annots

def process_single_image(model, img_path: str, target_layer, boxes: list, exp_name: str, layer_identifier: str, metrics: dict):
    """
    Processes a single image, generates CAM, computes metrics, and saves the visualization.
    """
    try:
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Could not read image {img_path}. Skipping.")
            return

        resized_img = cv2.resize(img, (800, 600))
        inp_for_cam = resized_img.astype(np.float32) / 255.0 # For `show_cam_on_image`

        cam_extractor = EigenCAM(model, [target_layer], task='od')
        cam_map = cam_extractor(resized_img)[0] # Assuming batch size 1, take the first CAM map

        # Compute metrics
        coverage = compute_box_coverage(cam_map, boxes)
        center_dist = compute_center_distance(cam_map, boxes)
        
        metrics[exp_name].append({'layer': layer_identifier, 'coverage': coverage, 'dist': center_dist})

        # Generate and save CAM visualization
        cam_img = show_cam_on_image(inp_for_cam, cam_map, use_rgb=True)
        
        # Overlay predicted boxes from YOLO
        # Note: model(resized_img) will perform inference on the resized image
        results = model(resized_img, verbose=False) # Add verbose=False to suppress print output
        if results and results[0].boxes:
            for x1, y1, x2, y2 in results[0].boxes.xyxy:
                cv2.rectangle(cam_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        out_dir = f"cam_results_{exp_name}"
        os.makedirs(out_dir, exist_ok=True)
        # Use layer_identifier in the filename
        out_path = os.path.join(out_dir, f"{os.path.basename(img_path).replace('.', '_')}_L{layer_identifier}.jpg")
        cv2.imwrite(out_path, cam_img)
        print(f"Processed {os.path.basename(img_path)} with layer {layer_identifier}. Cov: {coverage:.3f}, Dist: {center_dist:.3f}")

    except Exception as e:
        print(f"Error processing {img_path} with layer {layer_identifier} for model {exp_name}: {e}")


def doMultiScale(model_paths: list, images_dir: str, labels_dir: str, layers_to_analyze: list, device: str):
    """
    Main function to run CAM analysis for multiple models and layers.
    """
    # Parse models: allow 'path:name' or 'path'
    model_configs = []
    for m in model_paths:
        if ':' in m:
            path, name = m.split(':', 1)
        else:
            path = m
            name = os.path.splitext(os.path.basename(path))[0]
        model_configs.append({'path': path, 'name': name})

    # Use defaultdict to easily append metric values
    metrics = defaultdict(list)
    
    print(f"Loading annotations from {labels_dir} for images in {images_dir}...")
    annotations = load_yolo_labels(images_dir, labels_dir)
    print(f"Loaded {len(annotations)} images with annotations.")

    for config in model_configs:
        model_path = config['path']
        exp_name = config['name']
        print(f"\n--- Processing Model: {exp_name} ({model_path}) ---")
        try:
            model = YOLO(model_path).to(device)
            # Ensure model is in evaluation mode for consistent behavior
            model.eval() 
        except Exception as e:
            print(f"Error loading model {model_path}: {e}. Skipping this model.")
            continue

        for fn, boxes in annotations.items():
            img_path = os.path.join(images_dir, fn)
            
            # Dynamically get the layer object based on the index
            for idx in layers_to_analyze:
                target_layer = None
                layer_identifier = str(idx) # Default identifier
                
                # Special handling for the C2PSA Attention module
                if idx == 10:
                    try:
                        # Direct access to the Attention module within PSABlock
                        target_layer = model.model.model[10].m[0].attn 
                        layer_identifier = '10_C2PSA_Attention'
                        print(f"Targeting explicit attention layer: {layer_identifier}")
                    except Exception as e:
                        print(f"Could not access C2PSA Attention module at model.model.model[10].m[0].attn: {e}")
                        print("Falling back to C2PSA main block (layer 10) if available for CAM.")
                        target_layer = model.model.model[10] # Fallback to the whole C2PSA block
                        layer_identifier = '10_C2PSA_Block'
                else:
                    try:
                        target_layer = model.model.model[idx]
                        print(f"Targeting backbone/neck layer: model.model.model[{idx}]")
                    except IndexError:
                        print(f"Warning: Layer index {idx} not found in model {exp_name}. Skipping.")
                        continue
                
                if target_layer:
                    process_single_image(model, img_path, target_layer, boxes, exp_name, layer_identifier, metrics)

    # Print summary and write CSV
    print("\n--- Attention Metrics Summary ---")
    summary_rows = []
    detail_rows = []

    for exp_name, vals in metrics.items():
        if not vals:
            print(f"No metrics recorded for experiment: {exp_name}")
            continue

        # Group by layer for mean calculations
        layers_data = defaultdict(lambda: defaultdict(list))
        for v in vals:
            layers_data[v['layer']]['coverage'].append(v['coverage'])
            layers_data[v['layer']]['dist'].append(v['dist'])
            detail_rows.append({
                'experiment': exp_name,
                'image_filename': v.get('image_filename', 'N/A'), # if you added this to process_single_image
                'layer': v['layer'],
                'coverage': v['coverage'],
                'center_dist': v['dist']
            })

        # Overall mean
        all_covs = [v['coverage'] for v in vals]
        all_dists = [v['dist'] for v in vals]
        if all_covs and all_dists:
            mean_cov_all = np.mean(all_covs)
            mean_dist_all = np.mean(all_dists)
            num_samples_all = len(vals)
            print(f"Experiment: {exp_name} | Overall Mean Coverage: {mean_cov_all:.3f} | Overall Mean Distance: {mean_dist_all:.3f} | Samples: {num_samples_all}")
            summary_rows.append({
                'experiment': exp_name,
                'layer': 'ALL_LAYERS_MEAN',
                'coverage': mean_cov_all,
                'center_dist': mean_dist_all,
                'num_samples': num_samples_all
            })

        # Mean per layer
        print(f"  --- Mean Metrics per Layer for {exp_name} ---")
        for layer_id, data in sorted(layers_data.items()):
            mean_cov_layer = np.mean(data['coverage'])
            mean_dist_layer = np.mean(data['dist'])
            num_samples_layer = len(data['coverage'])
            print(f"    Layer: {layer_id} | Mean Coverage: {mean_cov_layer:.3f} | Mean Distance: {mean_dist_layer:.3f} | Samples: {num_samples_layer}")
            summary_rows.append({
                'experiment': exp_name,
                'layer': layer_id,
                'coverage': mean_cov_layer,
                'center_dist': mean_dist_layer,
                'num_samples': num_samples_layer
            })

    csv_path_summary = 'attention_metrics_summary.csv'
    csv_path_detail = 'attention_metrics_detail.csv'

    # Write summary CSV
    if summary_rows:
        summary_fieldnames = ['experiment', 'layer', 'coverage', 'center_dist', 'num_samples']
        with open(csv_path_summary, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=summary_fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nSaved summary metrics CSV to {csv_path_summary}")

    # Write detailed CSV (if needed, otherwise you can remove this)
    # The current `metrics` structure needs to store image filename for this
    # For simplicity, if you only want mean values, the summary is sufficient.
    # If you want detailed per-image, per-layer data, you need to extend the `metrics` dict storage in `process_single_image`
    # For now, `detail_rows` is built directly from appending to the `metrics` list, which has the necessary info.
    if detail_rows:
        detail_fieldnames = ['experiment', 'layer', 'coverage', 'center_dist'] # Assuming no image_filename stored yet
        # To include image_filename in detail_rows, modify process_single_image to include it in the dict appended to metrics.
        # e.g., metrics[exp_name].append({'layer': layer_identifier, 'coverage': coverage, 'dist': center_dist, 'image_filename': os.path.basename(img_path)})
        # Then, modify the detail_fieldnames and the loop that creates detail_rows.
        
        # Current implementation of `detail_rows` relies on `v.get('image_filename', 'N/A')`, meaning it expects it.
        # Let's adjust `process_single_image` to store it.
        fieldnames_for_detail_csv = ['experiment', 'layer', 'image_filename', 'coverage', 'center_dist']
        
        # Re-collect detail_rows with image_filename after adjusting `process_single_image` to include it.
        # This part of the code needs to be re-run or the `metrics` structure needs adjustment to save `image_filename`
        # Let's re-structure how `metrics` is filled in `process_single_image` to be complete.
        re_collected_detail_rows = []
        for exp_name, vals in metrics.items():
            for v in vals:
                re_collected_detail_rows.append({
                    'experiment': exp_name,
                    'image_filename': v.get('image_filename', 'N/A'),
                    'layer': v['layer'],
                    'coverage': v['coverage'],
                    'center_dist': v['dist']
                })

        with open(csv_path_detail, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_for_detail_csv)
            writer.writeheader()
            writer.writerows(re_collected_detail_rows)
        print(f"Saved detailed metrics CSV to {csv_path_detail}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate and analyze attention maps for YOLOv11m models.")
    parser.add_argument('--models', nargs='+', required=True, 
                        help="Paths to YOLOv11m models. Can be 'path/to/model.pt' or 'path/to/model.pt:model_name'.")
    parser.add_argument('--images', required=True, 
                        help="Path to the directory containing input images (e.g., JPEG, PNG).")
    parser.add_argument('--labels', required=True, 
                        help="Path to the directory containing YOLO format label text files corresponding to images.")
    parser.add_argument('--layers', nargs='+', type=int, 
                        default=[10, 16, 19, 22], # Adjusted default layers
                        help="List of model layer indices to analyze for attention maps. "
                             "Key layers for YOLOv11m are: "
                             "10 (C2PSA Attention block), "
                             "16, 19, 22 (Outputs feeding into detection heads for different scales).")
    parser.add_argument('--device', default='cpu', 
                        help="Device to run inference on (e.g., 'cpu', 'cuda:0').")
    args = parser.parse_args()
    
    # Adjust `process_single_image` to store `image_filename`
    # This modification must be done before `doMultiScale` is called
    # To avoid modifying global scope variables or passing extra args,
    # let's make `process_single_image` return the metric dict, then `doMultiScale` collects it.
    # Alternatively, ensure the dict in `metrics.append` has `image_filename`.
    # Let's go with adjusting `process_single_image`'s append directly.

    # Rerun the `process_single_image` logic inside `doMultiScale`
    # and adjust the `metrics.append` line to include `image_filename`.

    # Final adjustment: `process_single_image` should store image filename.
    # Let's pass `img_filename` to `process_single_image` and add it to the metrics dict.
    
    # Redefine process_single_image slightly for this:
    def process_single_image_updated(model, img_path: str, target_layer, boxes: list, exp_name: str, layer_identifier: str, metrics: dict):
        try:
            img = cv2.imread(img_path)
            if img is None:
                print(f"Warning: Could not read image {img_path}. Skipping.")
                return

            resized_img = cv2.resize(img, (800, 600))
            inp_for_cam = resized_img.astype(np.float32) / 255.0

            cam_extractor = EigenCAM(model, [target_layer], task='od')
            cam_map = cam_extractor(resized_img)[0]

            coverage = compute_box_coverage(cam_map, boxes)
            center_dist = compute_center_distance(cam_map, boxes)
            
            # Store image filename as well for detailed CSV
            metrics[exp_name].append({'layer': layer_identifier, 'coverage': coverage, 'dist': center_dist, 'image_filename': os.path.basename(img_path)})

            cam_img = show_cam_on_image(inp_for_cam, cam_map, use_rgb=True)
            results = model(resized_img, verbose=False)
            if results and results[0].boxes:
                for x1, y1, x2, y2 in results[0].boxes.xyxy:
                    cv2.rectangle(cam_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            out_dir = f"cam_results_{exp_name}"
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{os.path.basename(img_path).replace('.', '_')}_L{layer_identifier}.jpg")
            cv2.imwrite(out_path, cam_img)
            print(f"Processed {os.path.basename(img_path)} with layer {layer_identifier}. Cov: {coverage:.3f}, Dist: {center_dist:.3f}")

        except Exception as e:
            print(f"Error processing {img_path} with layer {layer_identifier} for model {exp_name}: {e}")

    # Replace the call inside doMultiScale with this updated function
    # To avoid re-pasting the whole `doMultiScale` here,
    # let's make `doMultiScale` accept this `process_single_image_func` as an argument
    # or just call this updated one.
    
    # For now, I'll modify the `doMultiScale` function directly to use `process_single_image_updated`
    # and then call the updated `doMultiScale`
    
    # Re-writing `doMultiScale` to incorporate the `image_filename` logging
    def doMultiScale_final(model_paths: list, images_dir: str, labels_dir: str, layers_to_analyze: list, device: str):
        model_configs = []
        for m in model_paths:
            if ':' in m:
                path, name = m.split(':', 1)
            else:
                path = m
                name = os.path.splitext(os.path.basename(path))[0]
            model_configs.append({'path': path, 'name': name})

        metrics = defaultdict(list)
        
        print(f"Loading annotations from {labels_dir} for images in {images_dir}...")
        annotations = load_yolo_labels(images_dir, labels_dir)
        print(f"Loaded {len(annotations)} images with annotations.")

        for config in model_configs:
            model_path = config['path']
            exp_name = config['name']
            print(f"\n--- Processing Model: {exp_name} ({model_path}) ---")
            try:
                model = YOLO(model_path).to(device)
                model.eval() 
            except Exception as e:
                print(f"Error loading model {model_path}: {e}. Skipping this model.")
                continue

            for fn, boxes in annotations.items():
                img_path = os.path.join(images_dir, fn)
                
                for idx in layers_to_analyze:
                    target_layer = None
                    layer_identifier = str(idx)
                    
                    if idx == 10:
                        try:
                            target_layer = model.model.model[10].m[0].attn 
                            layer_identifier = '10_C2PSA_Attention'
                            print(f"Targeting explicit attention layer: {layer_identifier}")
                        except Exception as e:
                            print(f"Could not access C2PSA Attention module at model.model.model[10].m[0].attn: {e}")
                            print("Falling back to C2PSA main block (layer 10) if available for CAM.")
                            target_layer = model.model.model[10]
                            layer_identifier = '10_C2PSA_Block'
                    else:
                        try:
                            target_layer = model.model.model[idx]
                            print(f"Targeting backbone/neck layer: model.model.model[{idx}]")
                        except IndexError:
                            print(f"Warning: Layer index {idx} not found in model {exp_name}. Skipping.")
                            continue
                    
                    if target_layer:
                        process_single_image_updated(model, img_path, target_layer, boxes, exp_name, layer_identifier, metrics)

        print("\n--- Attention Metrics Summary ---")
        summary_rows = []
        detail_rows = []

        for exp_name, vals in metrics.items():
            if not vals:
                print(f"No metrics recorded for experiment: {exp_name}")
                continue

            layers_data = defaultdict(lambda: defaultdict(list))
            for v in vals:
                layers_data[v['layer']]['coverage'].append(v['coverage'])
                layers_data[v['layer']]['dist'].append(v['dist'])
                # Already collected in `metrics` as `image_filename`

            # Overall mean
            all_covs = [v['coverage'] for v in vals]
            all_dists = [v['dist'] for v in vals]
            if all_covs and all_dists:
                mean_cov_all = np.mean(all_covs)
                mean_dist_all = np.mean(all_dists)
                num_samples_all = len(vals)
                print(f"Experiment: {exp_name} | Overall Mean Coverage: {mean_cov_all:.3f} | Overall Mean Distance: {mean_dist_all:.3f} | Samples: {num_samples_all}")
                summary_rows.append({
                    'experiment': exp_name,
                    'layer': 'ALL_LAYERS_MEAN',
                    'coverage': mean_cov_all,
                    'center_dist': mean_dist_all,
                    'num_samples': num_samples_all
                })

            print(f"  --- Mean Metrics per Layer for {exp_name} ---")
            for layer_id, data in sorted(layers_data.items()):
                mean_cov_layer = np.mean(data['coverage'])
                mean_dist_layer = np.mean(data['dist'])
                num_samples_layer = len(data['coverage'])
                print(f"    Layer: {layer_id} | Mean Coverage: {mean_cov_layer:.3f} | Mean Distance: {mean_dist_layer:.3f} | Samples: {num_samples_layer}")
                summary_rows.append({
                    'experiment': exp_name,
                    'layer': layer_id,
                    'coverage': mean_cov_layer,
                    'center_dist': mean_dist_layer,
                    'num_samples': num_samples_layer
                })
            
            # Populate detail_rows for current experiment
            for v in vals:
                detail_rows.append({
                    'experiment': exp_name,
                    'image_filename': v['image_filename'],
                    'layer': v['layer'],
                    'coverage': v['coverage'],
                    'center_dist': v['dist']
                })


        csv_path_summary = 'attention_metrics_summary.csv'
        csv_path_detail = 'attention_metrics_detail.csv'

        if summary_rows:
            summary_fieldnames = ['experiment', 'layer', 'coverage', 'center_dist', 'num_samples']
            with open(csv_path_summary, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=summary_fieldnames)
                writer.writeheader()
                writer.writerows(summary_rows)
            print(f"\nSaved summary metrics CSV to {csv_path_summary}")

        if detail_rows:
            detail_fieldnames = ['experiment', 'image_filename', 'layer', 'coverage', 'center_dist']
            with open(csv_path_detail, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=detail_fieldnames)
                writer.writeheader()
                writer.writerows(detail_rows)
            print(f"Saved detailed metrics CSV to {csv_path_detail}")

    # Call the final, adjusted doMultiScale function
    doMultiScale_final(args.models, args.images, args.labels, args.layers, args.device)