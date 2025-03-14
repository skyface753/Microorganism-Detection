ANZAHL_BILDER=3000
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
	python create_input_images_from_labelme.py --input_dir microorganism-dataset/ZKW_Data/fg_images --output_dir input/foregrounds --margin $(LABELME_MARGIN)

get-backgrounds:
	cp -r microorganism-dataset/ZKW_Data/backgrounds/* input/backgrounds

# extract-bboxes-from-labelme:
# 	python labelme_to_yolo_extractor.py --input_dir microorganism-dataset/ZKW_Data/fg_images/ \
# 	--output_dir additional_real_images_as_bboxes --labels Tardigrade

# either use the real images as additional backgrounds, or use them as a additional dataset
# TODO: when using as additional dataset, adjust the run command to include the additional dataset and the percentage of the additional dataset
bboxes-as-backgrounds:
	python labelme_to_yolo_extractor.py --input_dir microorganism-dataset/ZKW_Data/fg_images/ \
	--output_dir tmp --labels Tardigrade
	cp -r tmp/images/* input/backgrounds
	mkdir -p input/labels
	cp -r tmp/labels/* input/labels
	rm -rf tmp

prepare: create-folders clean-folders extract-from-labelme get-backgrounds bboxes-as-backgrounds



generate-images:
	python3 data_generation_yolo_backgrounds.py --input_dir input \
	--output_dir synthetic_images --image_number $(ANZAHL_BILDER) --yolo_output \
	--scaling_factors 0.25 0.85 --max_objects_per_image 4 --gaussian_options 9 9 \
	--fixed_image_sizes --parallelize --blending_methods alpha gaussian pyramid --yolo_input \
	--distractor_objects Mud


mix-datasets:
	python dataset_mixer.py --input_dirs 'synthetic_images' 'microorganism-dataset/clean_data' --test_dataset 'microorganism-dataset/ZKW_Data/test' \
	--percent_sets 90 10 --output_dir ready_dataset --class_names Tardigrade

run:
	python rain_model.py --dataset_dir 'ready_dataset' \
	--num_epochs 25 --results_dir 'results'

