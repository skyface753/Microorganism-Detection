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
	python create_input_images_from_labelme.py --input_dir dataset/ZKW_Data/fg_images --output_dir input/foregrounds --margin $(LABELME_MARGIN)

get-backgrounds:
	cp -r dataset/ZKW_Data/backgrounds/* input/backgrounds

prepare: create-folders clean-folders extract-from-labelme get-backgrounds

generate-images:
	python3 data_generation_yolo_backgrounds.py --input_dir input \
	--output_dir synthetic_images --image_number $(ANZAHL_BILDER) --yolo_output \
	--scaling_factors 0.25 0.85 --max_objects_per_image 4 --gaussian_options 9 9 \
	--fixed_image_sizes --parallelize --blending_methods alpha gaussian pyramid


run:
	python train_model.py --input_dirs 'synthetic_images' 'dataset/clean_data' --test_dataset 'dataset/ZKW_Data/test' \
	--dataset_dir 'ready_dataset' --results_dir 'results' -e 15
