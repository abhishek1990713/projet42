
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
    _, thresh = cv2.threshold(gray, 200, 255, 



    import os

# Assuming detect_skew_angle is defined elsewhere in your code

# Define the folder path containing the images
folder_path = 'path_to_your_folder'

# Loop through all the images in the folder
for filename in os.listdir(folder_path):
    # Check if the file is an image (you can modify this to include the extensions you need)
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(folder_path, filename)
        
        # Detect the skew angle
        detected_angle = detect_skew_angle(image_path)
        
        if detected_angle is not None:
            print(f"Image: {filename} - Detected skew angle: {detected_angle:.2f}°")
        else:
            print(f"Image: {filename} - No skew angle detected.")
