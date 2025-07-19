from ultralytics import YOLO
import cv2
import os
import argparse

RESIZE_WIDTH = 1920
RESIZE_HEIGHT = 1080


def visualize_and_display(image, results, window_name, save=False, savename=""):
    image = cv2.resize(image, (RESIZE_WIDTH, RESIZE_HEIGHT)
                       )  # Resize image to 800x600
    annotated_img = results[0].plot()
    # Resize annotated image to 800x600
    annotated_img = cv2.resize(annotated_img, (RESIZE_WIDTH, RESIZE_HEIGHT))

    num_objects = len(results[0].boxes) if hasattr(results[0], 'boxes') else 0

    FONT_SCALE = 2

    text = f"Detected objects: {num_objects}"
    text_size = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, 1)[0]
    text_x, text_y = 7, 25 * FONT_SCALE

    # Draw black rectangle as background for text
    # cv2.rectangle(annotated_img, (text_x - 5, text_y -
    #               text_size[1] - 5), (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
    # # Put white text on top of black rectangle
    # cv2.putText(annotated_img, text, (text_x, text_y),
    #             cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, (255, 255, 255), 1)
    if save:
        print(f"Saving annotated image to {savename}")
        # make folder if not exists
        os.makedirs(os.path.dirname(savename), exist_ok=True)
        cv2.imwrite(savename, annotated_img)
    else:
        cv2.imshow(window_name, annotated_img)


def save_images(models, model_names, img, img_path):
    for model, model_name in zip(models, model_names):
        # create a folder to save the output images
        os.makedirs("visualize_output", exist_ok=True)
        save_path = f"visualize_output/{model_name}_{os.path.basename(img_path)}"
        results = model(img)
        visualize_and_display(
            img, results, f'YOLOv11 Detection - {model_name}', save=True, savename=save_path)
    pass


def process_video(video_path, models, model_names):
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_idx = 0

    while cap.isOpened():
        if frame_idx < len(frames):
            frame = frames[frame_idx]
        else:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (800, 600))  # Resize frame to 800x600
            frames.append(frame)

        for model, model_name in zip(models, model_names):
            results = model(frame)
            visualize_and_display(
                frame, results, f'YOLOv11 Detection - {model_name}')

        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break
        elif key == 2:  # Left arrow key
            frame_idx = max(0, frame_idx - 1)
        elif key == ord('s'):
            save_images(models, model_names, frame, video_path)
            frame_idx += 1
        else:
            frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()


def process_images(image_folder, models, model_names):
    image_files = [os.path.join(image_folder, img)
                   for img in os.listdir(image_folder)]
    image_files = [img for img in image_files if cv2.imread(img) is not None]
    idx = 0

    while idx < len(image_files):
        img_path = image_files[idx]
        img = cv2.imread(img_path)
        img = cv2.resize(img, (800, 600))  # Resize image to 800x600

        for model, model_name in zip(models, model_names):
            results = model(img)
            visualize_and_display(
                img, results, f'YOLOv11 Detection - {model_name}', save=True, savename=f'visualize_output/{model_name}_{os.path.basename(img_path)}')

        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break
        elif key == 2:  # Left arrow key
            idx = max(0, idx - 1)
        elif key == ord('s'):
            save_images(models, model_names, img, img_path)
            idx += 1
        else:
            idx += 1

    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--images', type=str,
                        help='Path to folder containing images')
    parser.add_argument('--models', type=str, nargs='+',
                        help='Paths to YOLO models', required=True)
    args = parser.parse_args()

    print("Using models:", args.models)
    models = [YOLO(model_path) for model_path in args.models]
    model_names = [os.path.basename(model_path) for model_path in args.models]

    if args.video:
        process_video(args.video, models, model_names)
    elif args.images:
        process_images(args.images, models, model_names)
    else:
        print("Please provide either a video path or an image folder path.")


if __name__ == '__main__':
    main()