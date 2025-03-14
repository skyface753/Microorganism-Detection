import os
import cv2

valid_extensions = ('.jpg', '.png', '.JPG', '.PNG')


def replace_extension(file_name, new_extension):
    for ext in valid_extensions:
        if file_name.endswith(ext):
            return file_name[:file_name.rfind(ext)] + new_extension
    return file_name  # Return unchanged if no valid extension is found


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Show image or folder of images with ground truth and predicted bounding boxes')
    parser.add_argument('--input', type=str, required=True,
                        help='Either a directory containing images and labels or a single image')
    # parser.add_argument('--gt_labels', type=str, required=True,
    #                     help='Directory containing ground truth label files')
    parser.add_argument('--pred_labels', type=str, required=False,
                        help='Directory containing predicted label files')
    parser.add_argument('--write', type=bool, default=False,
                        help='Write the images with bounding boxes to a folder')
    parser.add_argument('--output', type=str, default='compare_bboxes_output',
                        help='Output folder to save the images with bounding boxes')
    parser.add_argument('--amount', type=int, default=10,
                        help='Amount of images to show (-1 for all)')
    parser.add_argument('--only_gt', type=bool, default=False,
                        help='Show only ground truth bounding boxes')
    parser.add_argument('--only_pred', type=bool, default=False,
                        help='Show only predicted bounding boxes')
    parser.add_argument('--classess', nargs='+', default=[],
                        help='Classes to show')

    args = parser.parse_args()

    if args.write and not os.path.exists(args.output):
        os.makedirs(args.output)

    input_path = args.input

    if os.path.isdir(input_path):
        if not os.path.exists(os.path.join(input_path, 'images')):
            print(
                f"Directory {input_path} does not contain a subdirectory named 'images'")
            exit()

        images = [f for f in os.listdir(os.path.join(
            input_path, 'images')) if f.endswith(valid_extensions)]
        images.sort()

        if args.amount != -1:
            images = images[:args.amount]
        for image in images:
            image_path = os.path.join(input_path, 'images', image)
            gt_label_path = os.path.join(
                input_path, 'labels', replace_extension(image, '.txt'))

            if os.path.exists(gt_label_path):
                print(f"Showing {image_path}")
                img = cv2.imread(image_path)
                height, width = img.shape[:2]

                def read_bboxes(label_path, color):
                    bboxes = []
                    if not os.path.exists(label_path):
                        return bboxes
                    with open(label_path, 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            bbox = line.split(' ')
                            class_id = int(bbox[0])
                            x_center = int(float(bbox[1]) * width)
                            y_center = int(float(bbox[2]) * height)
                            w = int(float(bbox[3]) * width)
                            h = int(float(bbox[4]) * height)
                            x1 = int(x_center - w / 2)
                            y1 = int(y_center - h / 2)
                            x2 = int(x_center + w / 2)
                            y2 = int(y_center + h / 2)
                            bboxes.append((class_id, x1, y1, x2, y2, color))
                    return bboxes

                gt_bboxes = []
                pred_bboxes = []
                if not args.only_pred:
                    # Green for ground truth
                    gt_bboxes = read_bboxes(gt_label_path, (0, 255, 0))
                    print(
                        f"Found {len(gt_bboxes)} ground truth bounding boxes")
                if args.pred_labels and not args.only_gt:
                    pred_label_path = os.path.join(
                        args.pred_labels, replace_extension(image, '.txt'))
                    pred_bboxes = read_bboxes(
                        pred_label_path, (0, 0, 255))  # Red for predictions

                for bbox in gt_bboxes + pred_bboxes:
                    class_id, x1, y1, x2, y2, color = bbox
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                    print(f"Bounding box: {x1}, {y1}, {x2}, {y2}")
                    if args.classess and args.classess != []:
                        class_name = args.classess[class_id]
                        cv2.putText(img, class_name, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                if args.write:
                    cv2.imwrite(os.path.join(args.output, image), img)
                else:
                    cv2.imshow(image_path, img)
                    if cv2.waitKey(0) & 0xFF == ord('q'):
                        quit()
                    cv2.destroyAllWindows()
            else:
                if not os.path.exists(gt_label_path):
                    print(f"Ground truth label file {gt_label_path} not found")
                if not os.path.exists(pred_label_path):
                    print(f"Predicted label file {pred_label_path} not found")
    else:
        print("Only directories with 'images' are supported in this version.")
