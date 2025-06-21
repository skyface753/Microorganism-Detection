import cv2
import numpy as np
from ultralytics import YOLO
from yolov11_cam.yolo_cam.eigen_cam import EigenCAM
from yolov11_cam.yolo_cam.utils.image import show_cam_on_image, scale_cam_image
import matplotlib.pyplot as plt
from PIL import Image

# DOWNLOAD THE GIT REPO
#
# git clone https://github.com/rigvedrs/YOLO-V11-CAM.git yolov11_cam
#


def process_single_image(model, imagePath, target_layer, show_bboxes=True):
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

    plt.imshow(cam_image)
    plt.show()


# multi scale CAM for yolov11 detection model, 16,19,22 represent small, medium, large object detect head of yolov11.
def doMultiScaleCAM(modelPath, imagePath, modelIndexes=[16, 19, 22]):
    """Perform multi-scale CAM using multiple target layers."""
    model = YOLO(modelPath)
    model = model.cpu()

    for i in modelIndexes:
        process_single_image(model, imagePath, model.model.model[i])

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
    image_path = 'additional_real_images_as_bboxes/images/Tardigrade_01_0002.png'
    # doMultiScaleCAM('best-t1-t4-models/best-t1.pt',
    #                 image_path, [16, 19, 22])
    # exit()

    model_weights = 'best-t1-t4-models/best-t1.pt'
    # model_weights = 'best-t1-t4-models/best-t4.pt'
    model = YOLO(model_weights)
    print(len(model.model.model))  # Check the number of layers in the model
    process_single_image(
        model,
        image_path,
        model.model.model[-2],
        show_bboxes=True)
