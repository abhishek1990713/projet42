

import os
import cv2
import random

# Input and Output directories
input_folder = "path/to/input/folder"   # Replace with your input folder path
output_folder = "path/to/output/folder" # Replace with your output folder path

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Rotation angles
rotation_angles = [30, 70, 90, 180, 220]

# Get list of image files
image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff'))]

# Process images
for img_file in image_files:
    img_path = os.path.join(input_folder, img_file)
    
    # Read the image
    image = cv2.imread(img_path)
    if image is None:
        print(f"Skipping {img_file}, unable to read image.")
        continue

    # Randomly decide whether to rotate
    if random.choice([True, False]):
        angle = random.choice(rotation_angles)
        
        # Get image dimensions and center
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)

        # Rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        # Save rotated image
        output_path = os.path.join(output_folder, f"rotated_{angle}_{img_file}")
        cv2.imwrite(output_path, rotated)
        print(f"Rotated {img_file} by {angle}° and saved to {output_path}")
    else:
        # Save without rotating
        output_path = os.path.join(output_folder, img_file)
        cv2.imwrite(output_path, image)
        print(f"Copied {img_file} without rotation.")

print("Processing completed!")
