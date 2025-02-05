import logging
import pandas as pd
from ultralytics import YOLO
from PIL import Image
import numpy as np
import re
from paddleocr import PaddleOCR
from japan_information_file import contants_info

# Configure logging
logging.basicConfig(
    filename="driving_lic_info.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize PaddleOCR
try:
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
    logger.info("PaddleOCR initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing PaddleOCR: {e}", exc_info=True)
    raise

# Driving license model path and expiration year limits
driving_license_model_path = contants_info.Driving_License_MODEL_PATH
MIN_EXPIRE_YEAR = contants_info.Min_expire_year
MAX_EXPIRE_YEAR = contants_info.Max_expire_year

def extract_year_from_dob(date_str):
    """Extract year from DOB date string, handling Japanese era if necessary."""
    try:
        year_match = re.search(r"(\d{4})年", date_str)
        if not year_match:
            era_match = re.search(r"(昭和|平成|令和)(\d{1,2})年", date_str)
            if era_match:
                era, era_year = era_match.groups()
                if era == "昭和":
                    year = 1926 + int(era_year)  # 昭和 starts in 1926
                elif era == "平成":
                    year = 1989 + int(era_year)  # 平成 starts in 1989
                elif era == "令和":
                    year = 2019 + int(era_year)  # 令和 starts in 2019
                else:
                    year = None
                return year
        else:
            return int(year_match.group(1))
    except Exception as e:
        logger.error(f"Error extracting year from DOB: {e}", exc_info=True)
        return None

def extract_year_from_expiration(date_str):
    """Extract year from expiration date string and convert Japanese era years to Gregorian years."""
    try:
        year_match = re.search(r"(\d{4})年", date_str)
        if not year_match:
            era_match = re.search(r"(昭和|平成|令和)(\d{1,2})年", date_str)
            if era_match:
                era, era_year = era_match.groups()
                if era == "昭和":
                    year = 1926 + int(era_year)
                elif era == "平成":
                    year = 1989 + int(era_year)
                elif era == "令和":
                    year = 2019 + int(era_year)
                else:
                    year = None
                return year
        else:
            return int(year_match.group(1))
    except Exception as e:
        logger.error(f"Error extracting year from expiration date: {e}", exc_info=True)
        return None

def process_dl_information(input_file_path):
    """Process driving license information from the input image file."""
    try:
        # Initialize the YOLO model with the driving license model path
        model = YOLO(driving_license_model_path)
        results = model(input_file_path)
        input_image = Image.open(input_file_path)
        
        # Initialize a list to collect the output data
        output_data = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                label = result.names[cls_id]
                bbox = box.xyxy[0].tolist()
                # Crop the image using the bounding box coordinates
                cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
                cropped_image_np = np.array(cropped_image)

                # Run OCR on the cropped image region
                result_texts = ocr.ocr(cropped_image_np, cls=False)
                if result_texts and result_texts[0]:
                    extracted_text = " ".join([text[1][0] for text in result_texts[0]])
                else:
                    extracted_text = ""

                logger.info(f"Detected {label}: {extracted_text}")

                # Add extracted information to the output data list
                output_data.append({
                    'Label': label,
                    'Extracted Text': extracted_text
                })

                # Extract and validate DOB
                if label == "DOB":
                    year = extract_year_from_dob(extracted_text)
                    if year:
                        logger.info(f"Extracted Year from DOB: {year}")
                        output_data.append({
                            'Label': 'Extracted Year from DOB',
                            'Extracted Text': year
                        })
                    else:
                        logger.warning(f"Could not extract valid year from DOB text: {extracted_text}")

                # Extract and validate expiration date
                if label == "Expiration date":
                    year = extract_year_from_expiration(extracted_text)
                    if year:
                        logger.info(f"Extracted Year from Expiration date: {year}")
                        output_data.append({
                            'Label': 'Extracted Year from Expiration date',
                            'Extracted Text': year
                        })
                        # Validate expiration year
                        if MIN_EXPIRE_YEAR <= year <= MAX_EXPIRE_YEAR:
                            output_data.append({
                                'Label': 'Expiration Year Validity',
                                'Extracted Text': f"Valid ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR})"
                            })
                        else:
                            output_data.append({
                                'Label': 'Expiration Year Validity',
                                'Extracted Text': f"Invalid ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR})"
                            })
                    else:
                        logger.warning(f"Could not extract valid year from Expiration date text: {extracted_text}")

        # Convert the output data list to a DataFrame
        df_output = pd.DataFrame(output_data)

        return df_output
    except Exception as e:
        logger.error(f"Error processing driving license information: {e}", exc_info=True)
        return None


