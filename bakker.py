
from ultralytics import YOLO
from PIL import Image
from datetime import datetime
import os
from paddleocr import PaddleOCR
import numpy as np
import logging
import re
import pandas as pd

# Suppress PaddleOCR logging warnings
logging.getLogger('ppocr').setLevel(logging.WARNING)

import contants_info  # Ensure this module is correctly defined

# Initialize PaddleOCR
ocr = PaddleOCR(
    lang='japan',
    use_angle_cls=False,
    use_gpu=False,
    det=True,
    rec=True,
    cls=False,
    det_model_dir=contants_info.DET_MODEL_DIR,
    rec_model_dir=contants_info.REC_MODEL_DIR,
    cls_model_dir=contants_info.CLS_MODEL_DIR
)

# Model Path
driving_license_model_path = r"C:\Users\AS34751\Downloads\dl_information"

# Expiration Year Limits
MIN_EXPIRE_YEAR = contants_info.Min_expire_year
MAX_EXPIRE_YEAR = contants_info.Max_expire_year

def extract_date_components(date_str):
    """Extracts year, month, and day from a Japanese date format."""
    match = re.search(r"(昭和|平成|令和)(\d{1,2})年(\d{1,2})月(\d{1,2})日", date_str)
    
    if match:
        era, era_year, month, day = match.groups()
        era_year, month, day = int(era_year), int(month), int(day)

        # Convert Japanese era year to Gregorian year
        if era == "昭和":
            year = 1925 + era_year  # 昭和 starts in 1926
        elif era == "平成":
            year = 1988 + era_year  # 平成 starts in 1989
        elif era == "令和":
            year = 2018 + era_year  # 令和 starts in 2019
        else:
            return None

        # Month names mapping
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }

        return {
            "Year": year,
            "Month": month_names.get(month, "Unknown"),
            "Day": day
        }
    
    return None

def process_dl_information(input_file_path):
    """Processes a driving license image and extracts relevant information."""
    model = YOLO(driving_license_model_path)
    results = model(input_file_path)
    input_image = Image.open(input_file_path)

    output = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            bbox = box.xyxy[0].tolist()
            
            # Crop image for OCR
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            cropped_image_np = np.array(cropped_image)
            
            result_texts = ocr.ocr(cropped_image_np, cls=False)
            extracted_text = "".join([text[1][0] for text in result_texts[0]]) if result_texts and result_texts[0] else ""

            print(f"Detected Label: {label}, Extracted Text: {extracted_text}")

            output.append({'Label': label, 'Extracted_Text': extracted_text})

            if label == "DOB":
                date_details = extract_date_components(extracted_text)
                if date_details:
                    logging.info(f"Extracted Date: {date_details}")
                    output.append({
                        "Label": "Extracted DOB",
                        "Extracted_Text": f"{date_details['Year']}-{date_details['Month']}-{date_details['Day']}"
                    })
                else:
                    logging.warning(f"Could not extract valid date from DOB: {extracted_text}")
                    output.append({"Label": "DOB Extraction Failed", "Extracted_Text": extracted_text})

            elif label == "Expiration date":
                date_details = extract_date_components(extracted_text)
                if date_details:
                    year = date_details['Year']
                    output.append({
                        "Label": "Extracted Expiration Year",
                        "Extracted_Text": year
                    })

                    # Validate expiration year
                    if MIN_EXPIRE_YEAR < year <= MAX_EXPIRE_YEAR:
                        output.append({
                            "Label": "Expiration Year Validity",
                            "Extracted_Text": f"Valid ({MIN_EXPIRE_YEAR} - {MAX_EXPIRE_YEAR})"
                        })
                    else:
                        output.append({
                            "Label": "Expiration Year Validity",
                            "Extracted_Text": f"Invalid ({MIN_EXPIRE_YEAR} - {MAX_EXPIRE_YEAR})"
                        })
                else:
                    logging.warning(f"Could not extract valid year from Expiration Date: {extracted_text}")
                    output.append({"Label": "Expiration Date Extraction Failed", "Extracted_Text": extracted_text})

    # Convert output to DataFrame
    data = pd.DataFrame(output)
    return data
