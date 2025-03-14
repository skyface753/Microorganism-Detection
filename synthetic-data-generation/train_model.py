from ultralytics import YOLO
import subprocess
import os


def run(dataset_dir, num_epochs, results_dir):

    model = YOLO("yolo11m.pt")
    train_res = model.train(data=f"{dataset_dir}/data.yaml", epochs=num_epochs, batch=0.8, save=True, seed=42, augment=True)

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    print("Result file:", str(train_res.save_dir) + "/results.png")
    subprocess.run(f'cp {str(train_res.save_dir)}/results.png {results_dir}/results.png', shell=True)
    subprocess.run(f'cp {str(train_res.save_dir)}/results.txt {results_dir}/results.txt', shell=True)
    subprocess.run(f'cp {train_res.save_dir}/weights/best.pt {results_dir}/best.pt', shell=True)


    test_res = model.val(data=f"{dataset_dir}/data.yaml", split="test")
    results_dict = test_res.results_dict
    # {'metrics/precision(B)': np.float64(0.5090883659171477), 'metrics/recall(B)': np.float64(0.5168539325842697), 'metrics/mAP50(B)': np.float64(0.5094240680500803), 'metrics/mAP50-95(B)': np.float64(0.31659841468085453), 'fitness': np.float64(0.33588098001777716)}
    mAP50 = results_dict["metrics/mAP50(B)"]
    mAP50_95 = results_dict["metrics/mAP50-95(B)"]
    print(mAP50)
    print(mAP50_95)
    # write to results file
    with open(f"{results_dir}/results.txt", "w") as f:
        f.write(f"MAP50: {mAP50}\n")
        f.write(f"MAP50-95: {mAP50_95}\n")
        
    print(f"Now you should copy the {results_dir}/best.pt to Object_Detection_Yolo_with_FastAPI/model.pt")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Train a YOLO model on a dataset')
    parser.add_argument('--dataset_dir', type=str,
                        help='Path to the dataset directory')
    parser.add_argument('--num_epochs', type=int,
                        help='Number of epochs to train the model')
    parser.add_argument('--results_dir', type=str,
                        help='Path to the results directory')
    args = parser.parse_args()
    
    run(args.dataset_dir, args.num_epochs, args.results_dir)
    