

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

                # Add validation for DOB and Expiration date
                if label == "DOB":
                    # Extract year, month, and day from the DOB text
                    dob_match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", extracted_text)
                    if dob_match:
                        year, month, day = int(dob_match.group(1)), int(dob_match.group(2)), int(dob_match.group(3))
                        # Validate DOB against current year and month
                        current_year = datetime.now().year
                        if year <= current_year:
                            output.append(f"DOB is valid: {year}-{month}-{day}")
                        else:
                            output.append(f"DOB is invalid: Year {year} is in the future.")
                    else:
                        output.append("DOB format is invalid.")

                elif label == "Expiration date":
                    # Extract year and month from the expiration date
                    expire_match = re.search(r"(\d{4})年(\d{1,2})月", extracted_text)
                    if expire_match:
                        year, month = int(expire_match.group(1)), int(expire_match.group(2))
                        current_date = datetime.now()
                        expiration_date = datetime(year, month, 1)

                        # Validate expiration date against valid range
                        if MIN_EXPIRE_YEAR <= year <= MAX_EXPIRE_YEAR:
                            if (year == MIN_EXPIRE_YEAR and month >= current_date.month) or year > MIN_EXPIRE_YEAR:
                                output.append(f"Expiration date is valid: {year}-{month}")
                            else:
                                output.append(f"Expiration date month is too early: {year}-{month}")
                            
                            # Check if expiration date has passed
                            if expiration_date < current_date:
                                output.append(f"Expiration date {year}-{month} has passed.")
                            else:
                                output.append(f"Expiration date {year}-{month} is still valid.")
                        else:
                            output.append(f"Expiration date year {year} is out of the valid range ({MIN_EXPIRE_YEAR}-{MAX_EXPIRE_YEAR}).")
                    else:
                        output.append("Expiration date format is invalid.")

    return output


# Test the implementation
if __name__ == "__main__":
    input_file_path = r"C:\CitiDev\Japan_pipeline\data_set\japan_test_image\6f7rch30 4.png"
    result = process_dl_information(input_file_path)
    print("\n".join(result))

