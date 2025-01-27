

from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import numpy as np
import re
import logging
from translation import initialize_models, translate_text
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
DRIVING_LICENSE_MODEL_PATH = r"C:\AS34751\Downloads\dl_information.pt"
LANG_MODEL_PATH = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
TRANSLATION_MODEL_PATH = r"C:\CitiDev\language_prediction\m2m"
MIN_EXPIRE_YEAR = 2024
MAX_EXPIRE_YEAR = 2032

# Initialize PaddleOCR
ocr = PaddleOCR(
    lang="japan",
    use_angle_cls=False,
    use_gpu=False,
    det=True,
    rec=True,
    cls=False
)

# Initialize translation models
lang_model, translation_pipeline = initialize_models(LANG_MODEL_PATH, TRANSLATION_MODEL_PATH)

def extract_date_details(date_str):
    """Extract year, month, and day from date string."""
    # Match format "2024年06月01日" or "昭和61年5月1日"
    year_match = re.search(r"(\d{4})年", date_str)
    month_match = re.search(r"(\d{1,2})月", date_str)
    day_match = re.search(r"(\d{1,2})日", date_str)
    
    # If it's a Japanese era (e.g., 昭和61年5月1日)
    if not year_match:
        era_match = re.search(r"(昭和|平成|令和)(\d{1,2})年", date_str)
        if era_match:
            era, era_year = era_match.groups()
            # Convert Japanese era year to AD
            if era == "昭和":
                year = 1926 + int(era_year)
            elif era == "平成":
                year = 1989 + int(era_year)
            elif era == "令和":
                year = 2019 + int(era_year)
            year_match = str(year)
    
    # Return extracted year, month, and day (as integers)
    if year_match and month_match and day_match:
        return int(year_match.group(1)), int(month_match.group(1)), int(day_match.group(1))
    return None, None, None

def process_dl_information(input_file_path):
    """Process driving license information using YOLO and OCR."""
    model = YOLO(DRIVING_LICENSE_MODEL_PATH)
    results = model(input_file_path)
    input_image = Image.open(input_file_path)
    output = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            bbox = box.xyxy[0].tolist()
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            cropped_image_np = np.array(cropped_image)

            result_texts = ocr.ocr(cropped_image_np, cls=False)
            extracted_text = (
                " ".join([text[1][0] for text in result_texts[0]])
                if result_texts and result_texts[0]
                else ""
            )

            logging.info(f"Detected {label}: {extracted_text}")
            output.append(f"Detected Label: {label}: {extracted_text}")

            # Translate the text if the label is "DOB" or "Expiration date"
            if label in ["DOB", "Expiration date"]:
                translated_text = translate_text([extracted_text], lang_model, translation_pipeline, target_language="en")[0]
                logging.info(f"Translated {label}: {translated_text}")
                output.append(f"Translated {label}: {translated_text}")

                # Extract month, day, and year from the text
                year, month, day = extract_date_details(extracted_text)
                if year and month and day:
                    logging.info(f"Extracted Year: {year}, Month: {month}, Day: {day}")
                    output.append(f"Extracted Year: {year}, Month: {month}, Day: {day}")
                
                    # Validate "Expiration date"
                    if label == "Expiration date":
                        if MIN_EXPIRE_YEAR <= year <= MAX_EXPIRE_YEAR:
                            output.append(f"Expiration year {year} is within the valid range ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR}).")
                        else:
                            output.append(f"Expiration year {year} is outside the valid range ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR}).")

                    # For DOB validation, check if the person is above 18 years old
                    if label == "DOB":
                        current_year = datetime.now().year
                        age = current_year - year
                        if age >= 18:
                            output.append(f"Age is valid: {age} years old.")
                        else:
                            output.append(f"Age is not valid: {age} years old. Must be 18 or older.")
                else:
                    output.append(f"Could not extract valid date details from {extracted_text}.")
                
            # Validate and process "Expiration date"
            if label == "Expiration date":
                year_match = re.search(r"\d{4}年", extracted_text)
                if year_match:
                    year = int(year_match.group(0).replace("年", ""))
                    output.append(f"Extracted Year: {year}")
                    if MIN_EXPIRE_YEAR <= year <= MAX_EXPIRE_YEAR:
                        output.append(f"Year {year} is within the valid range ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR}).")
                    else:
                        output.append(f"Year {year} is outside the valid range ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR}).")
                else:
                    output.append("Year not found in 'Expiration date' text.")

    return output


# Test the implementation
if __name__ == "__main__":
    input_file_path = r"C:\CitiDev\Japan_pipeline\data_set\japan_test_image\6f7rch30 4.png"
    result = process_dl_information(input_file_path)
    print("\n".join(result))
