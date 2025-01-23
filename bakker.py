project/
│
├── yolov5/                       # YOLOv5 repository (clone from GitHub)
├── data/                         # Dataset directory
│   ├── train/
│   │   ├── images/               # Training images
│   │   │   ├── img1.jpg
│   │   │   ├── img2.jpg
│   │   ├── labels/               # YOLO-format labels for training
│   │       ├── img1.txt
│   │       ├── img2.txt
│   ├── val/
│   │   ├── images/               # Validation images
│   │   │   ├── img3.jpg
│   │   │   ├── img4.jpg
│   │   ├── labels/               # YOLO-format labels for validation
│   │       ├── img3.txt
│   │       ├── img4.txt
│   ├── test/                     # Test data for inference (optional)
│       ├── images/
│           ├── img5.jpg
│           ├── img6.jpg
│
├── data.yaml                     # Dataset configuration file
├── incremental_training.py       # Training script
└── best.pt                       # Pre-trained YOLOv5 model (4-class model)
