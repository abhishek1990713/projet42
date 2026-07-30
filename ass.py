import os
import shutil
import random

# Source dataset
source_dir = "data"

# Output dataset
output_dir = "dataset"

# Train/Validation ratio
train_ratio = 0.7

# Supported image formats
image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")

random.seed(42)

classes = ["handwritten", "digital"]

for cls in classes:
    src_folder = os.path.join(source_dir, cls)

    images = [
        f for f in os.listdir(src_folder)
        if f.lower().endswith(image_extensions)
    ]

    random.shuffle(images)

    split_index = int(len(images) * train_ratio)

    train_images = images[:split_index]
    val_images = images[split_index:]

    train_folder = os.path.join(output_dir, "train", cls)
    val_folder = os.path.join(output_dir, "val", cls)

    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)

    # Copy train images
    for img in train_images:
        shutil.copy2(
            os.path.join(src_folder, img),
            os.path.join(train_folder, img)
        )

    # Copy validation images
    for img in val_images:
        shutil.copy2(
            os.path.join(src_folder, img),
            os.path.join(val_folder, img)
        )

    print(f"{cls}")
    print(f"  Total : {len(images)}")
    print(f"  Train : {len(train_images)}")
    print(f"  Val   : {len(val_images)}")

print("\nDataset split completed successfully!")
