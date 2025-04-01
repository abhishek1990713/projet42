
import cv2
import os
import numpy as np
import aspose.ocr as ocr

# Instantiate Aspose.OCR API
api = ocr.AsposeOCR()

def detect_skew_angle(image_path):
    """Detects the skew angle of a given image."""
    if not os.path.exists(image_path):
        print(f"X Error: File '{image_path}' not found.")
        return None

    print(f"Processing image: {image_path}")

    img = cv2.imread(image_path)

    if img is None:
        print("X Error: Unable to read the image file.")
        return None

    # Perform skew detection using AsposeOCR
    try:
        ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
        ocr_input.add(image_path)
        angles = api.calculate_skew(ocr_input)
    except RuntimeError as e:
        print(f"A Warning: Skew detection failed - {e}")
        return None

    if angles:
        skew_angle = angles[0].angle
        print(f"Skew Angle Detected = {skew_angle:.2f}")
        return skew_angle
    else:
        print("No skew detected")
        return None

def remove_background(image):
    """Removes the background using thresholding and contour detection."""
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding to create a binary image (foreground vs background)
    _, thresh 


import os
import pandas as pd

# Assuming detect_skew_angle is defined elsewhere in your code

def process_images_in_folders(main_folder, output_excel):
    data = []  # List to store results
    
    # Loop through all subfolders in the main folder
    for folder_name in os.listdir(main_folder):
        folder_path = os.path.join(main_folder, folder_name)
        
        # Check if it's a directory
        if os.path.isdir(folder_path):
            
            # Loop through all images in the subfolder
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(folder_path, filename)
                    
                    # Detect the skew angle
                    detected_angle = detect_skew_angle(image_path)
                    
                    # Append result to the list
                    data.append([folder_name, filename, detected_angle if detected_angle is not None else "No angle detected"])
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=['Folder Name', 'File Name', 'Detected Angle'])
    
    # Save to Excel
    df.to_excel(output_excel, index=False)
    print(f"Results saved to {output_excel}")

# Example usage
main_folder_path = "path_to_your_main_folder"
output_excel_path = "output.xlsx"
process_images_in_folders(main_folder_path, output_excel_path)
