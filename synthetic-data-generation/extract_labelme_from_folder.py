import os
import json
# get all .json files in the directory
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract labelme json files with images')
    parser.add_argument('--input_dir', type=str, required=True,
                        help='input directory containing labelme json files and images')
    parser.add_argument('--output_dir', type=str, required=True,
                        help='output directory to save the extracted json files with images')

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    for json_file in json_files:
        with open(os.path.join(input_dir, json_file), 'r') as f:
            json_data = json.load(f)
            image_name = json_data['imagePath']
            image_path = os.path.join(input_dir, image_name)
            print(f"Processing {json_file}")
            if os.path.exists(image_path):
                print(f"Found image {image_path}")
            else:
                print(f"Image {image_path} not found")
                continue
            output_path_json = os.path.join(output_dir, json_file)
            output_path_image = os.path.join(output_dir, image_name)
            with open(output_path_json, 'w') as f:
                json.dump(json_data, f)
            os.system(f"cp {image_path} {output_path_image}")
            print(f"Saved {output_path_json} and {output_path_image}")
