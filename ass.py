import os
import shutil

input_folder = "extract"
output_folder = "output"

os.makedirs(output_folder, exist_ok=True)

image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".gif", ".webp")

for folder_name in os.listdir(input_folder):
    folder_path = os.path.join(input_folder, folder_name)

    if os.path.isdir(folder_path):
        count = 0

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(image_extensions):
                    src = os.path.join(root, file)

                    # Rename file to avoid duplicate names
                    new_name = f"{folder_name}_{count + 1}{os.path.splitext(file)[1]}"
                    dest = os.path.join(output_folder, new_name)

                    shutil.copy2(src, dest)

                    count += 1
                    if count >= 5:
                        break
            if count >= 5:
                break

print("Done! Copied 5 images from each folder into the output folder.")
