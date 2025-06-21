import cv2
import numpy as np
from ultralytics import YOLO
from yolo_cam.eigen_cam import EigenCAM
from yolo_cam.utils.image import show_cam_on_image, scale_cam_image
import matplotlib.pyplot as plt
from PIL import Image
import os
import warnings

warnings.filterwarnings("ignore")

os.environ["ATEN_THREADED_TEST"] = "OFF"
# DOWNLOAD THE GIT REPO
#
# git clone https://github.com/rigvedrs/YOLO-V11-CAM.git yolov11_cam
# mv yolov11_cam/yolo_cam/ yolo_cam
# rm -rf yolov11_cam
#


def process_single_image(model, imagePath, target_layer, layer_index = -2, experiment_name = "", show_bboxes=True, write_to_disk=True):
    """Process a single image with a specific target layer and overlay bounding boxes."""
    img = cv2.imread(imagePath)
    img = cv2.resize(img, (800, 600))
    rgb_img = img.copy()
    img = np.float32(img) / 255

    cam = EigenCAM(model, [target_layer], task='od')
    grayscale_cam = cam(rgb_img)[0, :, :]
    cam_image = show_cam_on_image(img, grayscale_cam, use_rgb=True)

    # Perform object detection and overlay bounding boxes
    if show_bboxes:
        results = model(rgb_img)[0]
        for box in results.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(cam_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    
    if write_to_disk:
        # make directory if not exists
        folder = "cam_outputs"
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = f"{folder}/experiment_{experiment_name}_layer_{layer_index}.jpg"
        cv2.imwrite(filename, cam_image)
        print(f"CAM image saved to {filename}")
    else:
        plt.imshow(cam_image)
        plt.show()


# multi scale CAM for yolov11 detection model, 16,19,22 represent small, medium, large object detect head of yolov11.
def doMultiScaleCAM(modelPath, imagePath, modelIndexes=[16, 19, 22], experimentName="default"):
    """Perform multi-scale CAM using multiple target layers."""
    model = YOLO(modelPath)
    model = model.cpu()

    for i in modelIndexes:
        process_single_image(model, imagePath, model.model.model[i],
                            layer_index=i, experiment_name=experimentName,
                             show_bboxes=True, write_to_disk=True)

    img = cv2.imread(imagePath)
    img = cv2.resize(img, (800, 600))
    rgb_img = img.copy()
    im = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2RGB)
    res = model(rgb_img)[0]
    res = cv2.cvtColor(res.plot(), cv2.COLOR_BGR2RGB)
    a = Image.fromarray(np.hstack((im, res)))
    a.show()


# --- Example Usage ---
if __name__ == "__main__":
    image_path = 'microorganism-dataset/ZKW_Data/fg_images_as_bbox/images/Tardigrade_01_0008.png'
    model_weights = 'best-t1.pt'
    layers = [5, 8, 16, 19, 22]
    doMultiScaleCAM(model_weights,
                    image_path, layers, experimentName="t1-baseline")
    model_weights = 'best-t2.1-alpha/results/best.pt'
    doMultiScaleCAM(model_weights,
                    image_path, layers, experimentName="t2.1-alpha")
    model_weights = 'best-t2.2-gauss/results/best.pt'
    doMultiScaleCAM(model_weights,
                    image_path, layers, experimentName="t2.2-gauss")
    model_weights = 'best-t2.3-poisson/results/best.pt'
    doMultiScaleCAM(model_weights,
                    image_path, layers, experimentName="t2.3-poisson")
    model_weights = 'best-t2.4-pyramid/results/best.pt'
    doMultiScaleCAM(model_weights,
                    image_path, layers, experimentName="t2.4-pyramid")
    model_weights = 'best-t3-multi/results/best.pt'
    doMultiScaleCAM(model_weights,
                    image_path, layers, experimentName="t3-multi")

    # model_weights = 'best-t1-t4-models/best-t4.pt'
    # model = YOLO(model_weights)
    # print(len(model.model.model))  # Check the number of layers in the model
    # process_single_image(
    #     model,
    #     image_path,
    #     model.model.model[-2],
    #     image_name="-2",
    #     show_bboxes=True)
