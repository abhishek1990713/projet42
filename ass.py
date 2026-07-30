import os
import shutil

# Input and output folders
input_folder = "extract"
output_folder = "output"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Supported image extensions
image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".gif", ".webp")

count = 0

# Walk through all folders and subfolders
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.lower().endswith(image_extensions):
            source_path = os.path.join(root, file)

            # Handle duplicate file names
            destination_path = os.path.join(output_folder, file)
            if os.path.exists(destination_path):
                name, ext = os.path.splitext(file)
                destination_path = os.path.join(output_folder, f"{name}_{count}{ext}")

            shutil.copy2(source_path, destination_path)
            count += 1

print(f"Done! Copied {count} images to '{output_folder}' folder.")
