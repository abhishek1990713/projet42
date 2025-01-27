

from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import numpy as np
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
DRIVING_LICENSE_MODEL_PATH = r"C:\AS34751\Downloads\dl_information.pt"
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

def extract_year_from_dob(date_str):
    """Extract year from DOB string and convert Japanese era years to Gregorian years."""
    # Match format "昭和61年5月1日" or "平成30年6月2日"
    year_match = re.search(r"(\d{4})年", date_str)
    
    # If it's a Japanese era (e.g., 昭和61年5月1日)
    if not year_match:
        era_match = re.search(r"(昭和|平成|令和)(\d{1,2})年", date_str)
        if era_match:
            era, era_year = era_match.groups()
            # Convert Japanese era year to AD
            if era == "昭和":
                year = 1926 + int(era_year)  # 昭和 starts in 1926
            elif era == "平成":
                year = 1989 + int(era_year)  # 平成 starts in 1989
            elif era == "令和":
                year = 2019 + int(era_year)  # 令和 starts in 2019
            return year
    
    # Return extracted year if matched
    if year_match:
        return int(year_match.group(1))
    
    return None

def extract_year_from_expiration(date_str):
    """Extract year from expiration date string and convert Japanese era years to Gregorian years."""
    # Match format "2024年06月01日" or "令和06年6月1日"
    year_match = re.search(r"(\d{4})年", date_str)
    
    # If it's a Japanese era (e.g., 令和06年6月1日)
    if not year_match:
        era_match = re.search(r"(昭和|平成|令和)(\d{1,2})年", date_str)
        if era_match:
            era, era_year = era_match.groups()
            # Convert Japanese era year to AD
            if era == "昭和":
                year = 1926 + int(era_year)  # 昭和 starts in 1926
            elif era == "平成":
                year = 1989 + int(era_year)  # 平成 starts in 1989
            elif era == "令和":
                year = 2019 + int(era_year)  # 令和 starts in 2019
            return year
    
    # Return extracted year if matched
    if year_match:
        return int(year_match.group(1))
    
    return None

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

            # Extract year from the text (DOB or Expiration date)
            if label == "DOB":
                year = extract_year_from_dob(extracted_text)
                if year:
                    logging.info(f"Extracted Year from DOB: {year}")
                    output.append(f"Extracted Year from DOB: {year}")
                else:
                    output.append(f"Could not extract valid year from DOB text: {extracted_text}")
                
            if label == "Expiration date":
                year = extract_year_from_expiration(extracted_text)
                if year:
                    logging.info(f"Extracted Year from Expiration date: {year}")
                    output.append(f"Extracted Year from Expiration date: {year}")
                    # Validate expiration year
                    if MIN_EXPIRE_YEAR <= year <= MAX_EXPIRE_YEAR:
                        output.append(f"Expiration year {year} is within the valid range ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR}).")
                    else:
                        output.append(f"Expiration year {year} is outside the valid range ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR}).")
                else:
                    output.append(f"Could not extract valid year from Expiration date text: {extracted_text}")

    return output


# Test the implementation
if __name__ == "__main__":
    input_file_path = r"C:\CitiDev\Japan_pipeline\data_set\japan_test_image\6f7rch30 4.png"
    result = process_dl_information(input_file_path)
    print("\n".join(result))
