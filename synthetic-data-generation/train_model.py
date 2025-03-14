import subprocess
import os
import torch
from ultralytics import YOLO
import re


def create_dataset(input_dirs, test_dataset, output_dir, p):
    o_dir = f'{output_dir}'
    in_dirs = ' '.join(input_dirs)
    ps = ' '.join([str(x) for x in p])
    if len(input_dirs) == 1:
        ps = f'100'
    # --fixed_data_path /home/jovyan/work/'
    cmd = f'python dataset_mixer.py --input_dirs {in_dirs} --test_dataset {test_dataset} --percent_sets {ps} --output_dir {o_dir} --class_names Tardigrade'
    print(cmd)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # try to create the dataset
    if subprocess.run(cmd, shell=True).returncode != 0:
        print('Error in creating dataset')
        quit()
    return o_dir


def get_num_images(path):
    if os.path.exists(f"{path}/num_images.txt"):
        with open(f"{path}/num_images.txt", "r") as f:
            lines = f.readlines()
            train_images = int(lines[0].split(":")[1].strip())
            valid_images = int(lines[1].split(":")[1].strip())
            test_images = int(lines[2].split(":")[1].strip())
            print(f"found {train_images} train images in {path}")
    else:
        # get the paths from the data.yaml
        with open(f"{path}/data.yaml", "r") as f:
            data = f.read()
            # path starts with train, val, test
            try:
                train_images_path = re.search(r"train: (.*)", data).group(1)
                valid_images_path = re.search(r"val: (.*)", data).group(1)
                test_images_path = re.search(r"test: (.*)", data).group(1)
                if train_images_path.startswith("../"):
                    train_images_path = train_images_path[3:]
                if valid_images_path.startswith("../"):
                    valid_images_path = valid_images_path[3:]
                if test_images_path.startswith("../"):
                    test_images_path = test_images_path[3:]

                # make path absolute, if it is not
                if not train_images_path.startswith("/"):
                    train_images_path = os.path.abspath(
                        os.path.join(path, train_images_path))
                if not valid_images_path.startswith("/"):
                    valid_images_path = os.path.abspath(
                        os.path.join(path, valid_images_path))
                if not test_images_path.startswith("/"):
                    test_images_path = os.path.abspath(
                        os.path.join(path, test_images_path))
                train_images = len(os.listdir(f"{train_images_path}"))
                valid_images = len(os.listdir(f"{valid_images_path}"))
                test_images = len(os.listdir(f"{test_images_path}"))
                print(
                    f"found {train_images} train images in {train_images_path}")
            except Exception as e:
                print("Error in reading data.yaml")
                print(e)
                train_images = 0
                valid_images = 0
                test_images = 0
    return train_images, valid_images, test_images


def run_test(path, OUT_DIR, ANZAHL_EPOCHEN, save_whole_folder=False):
    print(f"Training dataset: {path}")
    # anzahl der bilder
    train_images, valid_images, test_images = get_num_images(path)
    print("Found following images in dataset:")
    print(f"Train images: {train_images}")
    print(f"Valid images: {valid_images}")
    print(f"Test images: {test_images}")
    model = YOLO("yolo11m.pt")
    train_res = model.train(
        data=f"{path}/data.yaml", epochs=ANZAHL_EPOCHEN, batch=0.8, save=True, seed=42, augment=True)
    test_res = model.val(data=f"{path}/data.yaml",
                         split="test", save_json=True, plots=True)

    results_dict = test_res.results_dict
    # {'metrics/precision(B)': np.float64(0.5090883659171477), 'metrics/recall(B)': np.float64(0.5168539325842697), 'metrics/mAP50(B)': np.float64(0.5094240680500803), 'metrics/mAP50-95(B)': np.float64(0.31659841468085453), 'fitness': np.float64(0.33588098001777716)}
    mAP50 = results_dict["metrics/mAP50(B)"]
    mAP50_95 = results_dict["metrics/mAP50-95(B)"]

    with open(f"{OUT_DIR}/results.txt", "w") as f:
        f.write(f"Train images: {train_images}\n")
        f.write(f"Valid images: {valid_images}\n")
        f.write(f"Test images: {test_images}\n")
        f.write(f"----------------------------------\n")
        f.write(f"MAP50: {mAP50}\n")
        f.write(f"MAP50-95: {mAP50_95}\n")
        f.write(f"results_dict: {str(results_dict)}")
    del model
    try:
        torch.cuda.empty_cache()
    except:
        pass
    if save_whole_folder:
        subprocess.run(
            f'zip -r {OUT_DIR}/train_results.zip {train_res.save_dir}', shell=True)
        subprocess.run(
            f'zip -r {OUT_DIR}/test_results.zip {test_res.save_dir}', shell=True)
    # delete the train and test results
    subprocess.run(f"rm -r {train_res.save_dir}", shell=True)
    subprocess.run(f"rm -r {test_res.save_dir}", shell=True)
    return mAP50, mAP50_95


def clean_folder(path):
    try:
        subprocess.run(f"rm -r {path}", shell=True)
    except:
        pass
    os.makedirs(path, exist_ok=True)


def run(input_dirs, test_dataset, DATASET_DIR, RESULTS_DIR, ANZAHL_EPOCHEN, percentages):
    # check if the folder exists
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    # wait for input, if the folder is not empty
    if len(os.listdir(DATASET_DIR)) > 0 or len(os.listdir(RESULTS_DIR)) > 0:
        print(
            "Dataset or Results folder not empty. They will be cleaned! Continue? [y/n/skip]")
        answer = input()
        if answer == "y":
            clean_folder(DATASET_DIR)
            clean_folder(RESULTS_DIR)
        elif answer == "skip":
            pass
        else:
            print("Exiting")
            quit()

    dir = create_dataset(input_dirs, test_dataset, DATASET_DIR, percentages)

    run_test(
        dir, RESULTS_DIR, ANZAHL_EPOCHEN, save_whole_folder=True)

    # subprocess.run(f"rm -r {dir}", shell=True)


def validate_percentages(percentages, input_dirs):
    if len(percentages) == 0:
        print("No percentages given")
        quit()
    if len(percentages) != len(input_dirs):
        print("Number of percentages does not match number of input directories")
        print(f"Percentages: {percentages}")
        print(f"Input directories: {input_dirs}")
        quit()
    if sum(percentages) != 100:
        print("Percentages do not sum up to 100")
        print(f"Percentages: {percentages}")
        quit()
    return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='RUN training with specified percentage')
    parser.add_argument('--input_dirs', nargs='+', help='Input directories')
    parser.add_argument('--test_dataset', help='Test dataset')
    parser.add_argument('--dataset_dir', help='Dataset directory')
    parser.add_argument('--results_dir', help='Results directory')
    # anzahl epochen
    parser.add_argument('-e', '--anzahl_epochen', type=int, default=15,
                        help='Number of epochs')
    percentages = [90, 10]
    parser.add_argument('--percentages', nargs='+', type=int, default=percentages,
                        help='Percentages of the datasets')
    args = parser.parse_args()

    # parse the percentages
    print(f'Received percentages: {args.percentages}')
    percentages = args.percentages
    validate_percentages(percentages, args.input_dirs)

    run(args.input_dirs, args.test_dataset, args.dataset_dir,
        args.results_dir, args.anzahl_epochen, percentages)
