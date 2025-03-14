Download the dataset:

```bash
kaggle datasets download -p microorganism-dataset sebastianjrz/microorganism-dataset --unzip
```

Files:

| File Name                             | Description                                                                                            |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `data_generation_yolo_backgrounds.py` | Script to generate synthetic data using YOLO format                                                    |
| `create_input_images_from_labelme.py` | Script to extract labelme polygons into foreground images                                              |
| `dataset_mixer.py`                    | Script to mix multiple datasets into one (eg. synthetic images and real images)                        |
| `labelme_to_yolo_extractor.py`        | Script to convert labelme polygons into YOLO format (eg. use as additional real images)                |
| `train_model.py`                      | Script to train a model using synthetic and real data (using the `dataset_mixer.py` script internally) |
