import os
import cv2
import numpy as np
import argparse


def resize_images(input_folder, output_folder, target_size=(256, 256)):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        if not os.path.isfile(input_path):
            continue

        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            continue

        if image.shape[-1] == 4:  # Check if image has an alpha channel
            alpha_channel = image[:, :, 3]
            image = image[:, :, :3]  # Remove alpha channel
            # Set transparent pixels to black
            image[alpha_channel == 0] = [0, 0, 0]

        h, w = image.shape[:2]
        scale = min(target_size[0] / w, target_size[1] / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(image, (new_w, new_h),
                             interpolation=cv2.INTER_AREA)

        padded = np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
        y_offset = (target_size[1] - new_h) // 2
        x_offset = (target_size[0] - new_w) // 2
        padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

        cv2.imwrite(output_path, padded)
        print(f"Processed {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize images in a folder.")
    parser.add_argument("--input", type=str, required=True,
                        help="Path to the input folder containing images.")
    parser.add_argument("--output", type=str, required=True,
                        help="Path to the output folder to save resized images.")
    parser.add_argument("--size", type=int, nargs=2, default=(256, 256),
                        help="Target size for resizing images (width, height).")
    args = parser.parse_args()
    input_folder = args.input
    output_folder = args.output
    target_size = args.size
    resize_images(input_folder, output_folder, target_size)
