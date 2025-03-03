
import os
import re
import logging
import numpy as np
from PIL import Image
import pytesseract
from ultralytics import YOLO
from passport_test import parse_mrz  # Import MRZ parser

# Set Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Set logging level
logging.getLogger("ppocr").setLevel(logging.WARNING)

# Load YOLO model
model_path = r"C:\Users\AS34751\Downloads\test.pt"
model = YOLO(model_path)

# Function to process passport image and extract MRZ
def process_passport_image(input_file_path, confidence_threshold=0.70):
    input_image = Image.open(input_file_path)

    # Run YOLO on the image
    results = model(input_file_path)

    # Initialize MRZ lines
    mrl_one = None
    mrl_second = None

    for result in results:
        boxes = result.boxes

        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names.get(cls_id, f"class_{cls_id}")  # Get class name
            
            # Extract bounding box coordinates
            bbox = box.xyxy[0].tolist()

            # Crop detected region
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

            # Perform OCR on cropped image
            ocr_text = pytesseract.image_to_string(cropped_image).strip()
            print(f"OCR Text for {label}: {ocr_text}")

            # Assign MRZ lines
            if label == "MRL_ONE":
                mrl_one = ocr_text.replace(" ", "").replace("\n", "")  # Remove spaces/newlines
            elif label == "MRL_SECOND":
                mrl_second = ocr_text.replace(" ", "").replace("\n", "")

    # If both MRZ lines are found, parse them
    if mrl_one and mrl_second:
        passport_info = parse_mrz(mrl_one, mrl_second)
        return passport_info
    else:
        return {"Error": "MRZ lines not fully detected"}

# Example usage
if __name__ == "__main__":
    input_file_path = "path_to_your_passport_image.jpg"  # Update this with actual image path
    output = process_passport_image(input_file_path)
    print(output)
