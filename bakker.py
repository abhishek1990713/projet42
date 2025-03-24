⁸

mrl1 = 


import os
import cv2
import numpy as np
import aspose.ocr as ecr  # Aspose OCR for skew detection

def correct_skew(image, angle):
    """Correct skew using OpenCV rotation based on the detected angle."""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected

# Initialize Aspose.OCR API
api = ecr.AsposeOCR()

# File path (Update this to your file location)
file_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\Skewed- Payment advice.tiff"

# Define output folder
output_folder = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Output"
os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist

# Detect if it's an image, TIFF, or PDF
if file_path.lower().endswith(".pdf"):
    input_type = ecr.InputType.PDF
elif file_path.lower().endswith((".tiff", ".tif", ".png", ".jpg", ".jpeg")):
    input_type = ecr.InputType.SINGLE_IMAGE
else:
    raise ValueError("Unsupported file format!")

# Add file to OCR batch
ocr_input = ecr.OcrInput(input_type)
ocr_input.add(file_path)

# Detect skew angles using Aspose
angles = api.calculate_skew(ocr_input)

if angles:
    best_angle = angles[0].angle  # Use first detected angle
    print(f"Detected Skew Angle: {best_angle:.1f}°")

    if input_type == ecr.InputType.SINGLE_IMAGE:
        # Load the image (TIFF, PNG, JPG, etc.)
        image = cv2.imread(file_path)

        if image is None:
            print("Error: Could not read image. Ensure the file path is correct.")
        else:
            corrected_image = correct_skew(image, best_angle)

            # Save the corrected image in the output folder
            file_name = os.path.basename(file_path)
            save_path = os.path.join(output_folder, f"corrected_{file_name}")
            cv2.imwrite(save_path, corrected_image)

            print("Corrected image saved at:", save_path)

            cv2.imshow("Corrected Image", corrected_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("PDF detected! Skew correction for PDFs requires further processing.")
else:
    print("No skew detected.")

