import os
import re
import logging
import pandas as pd  # Import pandas for DataFrame
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
from ultralytics import YOLO
from passport_test import parse_mrz  # Import MRZ parsing function

# Suppress unnecessary logging
logging.getLogger("ppocr").setLevel(logging.WARNING)

# Initialize PaddleOCR (English and numeric mode for MRZ)
ocr_model = PaddleOCR(use_angle_cls=False, lang="en")

# Load YOLO model for passport MRZ detection
model_path = r"C:\Users\AS34751\Downloads\test.pt"
model = YOLO(model_path)

def process_passport_image(input_file_path, confidence_threshold=0.70):
    """Processes a passport image, extracts MRZ text using PaddleOCR, and returns passport details as a DataFrame."""

    # Load input image
    input_image = Image.open(input_file_path)
    results = model(input_file_path)  # YOLO object detection

    # Initialize variables
    extracted_data = []  # Store detected labels and OCR text
    mrl1, mrl2 = None, None  # MRZ lines

    for result in results:
        boxes = result.boxes  # Detected bounding boxes

        for box in boxes:
            cls_id = int(box.cls[0])  # Class ID
            label = result.names.get(cls_id, "Unknown")  # Label name
            confidence = box.conf[0].item()  # Extract confidence score

            # Apply confidence threshold filter
            if confidence < confidence_threshold:
                print(f"Skipping {label} (Confidence: {confidence:.2f})")
                continue

            # Extract bounding box coordinates
            bbox = box.xyxy[0].tolist()
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

            # Convert image to numpy array for OCR processing
            cropped_image_np = np.array(cropped_image)

            # Perform OCR using PaddleOCR
            ocr_results = ocr_model.ocr(cropped_image_np, cls=False)

            # Extract text from OCR results with confidence check
            extracted_text = ""
            for line in ocr_results:
                for word in line:
                    word_text, word_confidence = word[1][0], word[1][1]
                    if word_confidence >= confidence_threshold:
                        extracted_text += word_text

            print(f"Detected {label} (Confidence: {confidence:.2f}): {extracted_text}")

            # Store extracted text and label in the list
            extracted_data.append({"Label": label, "Extracted Text": extracted_text, "Confidence": confidence})

            # Assign extracted text based on label (MRL_ONE or MRL_SECOND)
            if "MRL_ONE" in label.upper():
                mrl1 = extracted_text
            elif "MRL_SECOND" in label.upper():
                mrl2 = extracted_text

    # Create a DataFrame with detected text and labels
    detected_df = pd.DataFrame(extracted_data)

    # Ensure both MRZ lines are extracted
    if mrl1 and mrl2:
        passport_info = parse_mrz(mrl1, mrl2)  # Parse MRZ details

        # Convert extracted passport info into a DataFrame
        passport_df = pd.DataFrame([passport_info])

        # Merge detected data and passport info
        final_df = pd.concat([detected_df, passport_df], axis=1)
        return final_df
    else:
        return pd.DataFrame([{"Error": "Failed to extract MRZ lines with sufficient confidence"}])

# Example Usage
if __name__ == "__main__":
    image_path = r"C:\path\to\passport_image.jpg"  # Replace with actual image path
    passport_df = process_passport_image(image_path)

    print("\nExtracted Passport Information (DataFrame):")
    print(passport_df)
