import os

# Parameters
PRETRAINED_WEIGHTS = "yolov5s.pt"  # Path to pre-trained weights (e.g., COCO-trained model or previous model)
DATA_YAML = "data.yaml"           # Path to the dataset YAML file
OUTPUT_DIR = "runs/train"         # Directory to save the results
EPOCHS = 10                       # Number of training epochs
BATCH_SIZE = 16                   # Batch size for training
IMG_SIZE = 640                    # Image size for training and validation
FREEZE_LAYERS = 10                # Number of layers to freeze during training (set to 0 if not needed)

# Training command
train_command = f"""
python train.py --img {IMG_SIZE} \
                --batch {BATCH_SIZE} \
                --epochs {EPOCHS} \
                --data {DATA_YAML} \
                --weights {PRETRAINED_WEIGHTS} \
                --project {OUTPUT_DIR}
"""

# Add optional layer freezing
if FREEZE_LAYERS > 0:
    train_command += f" --freeze {FREEZE_LAYERS}"

# Run training
print("Starting YOLOv5 training...")
os.system(train_command)

# Validate the model after training
BEST_WEIGHTS_PATH = os.path.join(OUTPUT_DIR, "exp", "weights", "best.pt")
print("Validating the model...")
validate_command = f"""
python val.py --weights {BEST_WEIGHTS_PATH} \
              --data {DATA_YAML} \
              --img {IMG_SIZE}
"""
os.system(validate_command)

# Perform inference on test images
INFERENCE_SOURCE = "data/test/images"  # Path to a folder containing test images
print("Running inference on test images...")
inference_command = f"""
python detect.py --weights {BEST_WEIGHTS_PATH} \
                 --source {INFERENCE_SOURCE} \
                 --img {IMG_SIZE}
"""
os.system(inference_command)

print("Incremental training, validation, and inference complete.")


