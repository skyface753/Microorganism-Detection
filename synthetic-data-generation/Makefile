ANZAHL_BILDER=3420
LABELME_MARGIN=20


create-folders:
	mkdir -p input/foregrounds
	mkdir -p input/backgrounds
	mkdir -p synthetic_images
	mkdir -p ready_dataset
	mkdir -p results

clean-folders:
	rm -rf input/foregrounds/*
	rm -rf input/backgrounds/*
	rm -rf synthetic_images/*
	rm -rf ready_dataset/*
	rm -rf results/*

extract-from-labelme:
	uv run SynDataGenYOLO extract --input_dir microorganism-dataset/ZKW_Data/fg_images --output_dir input/foregrounds --margin $(LABELME_MARGIN)

get-backgrounds:
	cp -r microorganism-dataset/ZKW_Data/backgrounds/* input/backgrounds

# extract-bboxes-from-labelme:
# 	python labelme_to_yolo_extractor.py --input_dir microorganism-dataset/ZKW_Data/fg_images/ \
# 	--output_dir additional_real_images_as_bboxes --labels Tardigrade

# either use the real images as additional backgrounds, or use them as a additional dataset
# TODO: when using as additional dataset, adjust the run command to include the additional dataset and the percentage of the additional dataset
bboxes-as-backgrounds:
	uv run SynDataGenYOLO extract_yolo --input_dir microorganism-dataset/ZKW_Data/fg_images/ \
	--output_dir tmp --labels Tardigrade
	cp -r tmp/images/* input/backgrounds
	mkdir -p input/labels
	cp -r tmp/labels/* input/labels
	rm -rf tmp

prepare: create-folders clean-folders extract-from-labelme get-backgrounds bboxes-as-backgrounds



generate-images:
	uv run SynDataGenYOLO generate --input_dir input --augmentation_path transform.yml \
	--output_dir synthetic_images --image_number $(ANZAHL_BILDER) --output_mode YOLO \
	--scaling_factors 0.25 0.85 --max_objects_per_image 4 --gaussian_options 9 9 \
	--fixed_image_sizes --parallelize --blending_methods alpha gaussian pyramid --yolo_input \
	--distractor_objects Mud


mix-datasets:
	uv run SynDataGenYOLO mix --input_dirs 'synthetic_images' 'microorganism-dataset/all_real' --test_dataset 'microorganism-dataset/ZKW_Data/test' \
	--percent_sets 60 40 --output_dir ready_dataset --class_names Tardigrade

run:
	python train_model.py --dataset_dir 'ready_dataset' \
	--num_epochs 25 --results_dir 'results'

