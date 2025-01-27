
from ultralytics import YOLO
from PIL import Image
from paddleocr import PaddleOCR
import numpy as np
import re
import logging
from translation import initialize_models, translate_text

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

            # Append the detected label and original text
            output.append(f"Detected {label}: {extracted_text}")

            # Translate and format the text for "DOB" or "Expiration date"
            if label in ["DOB", "Expiration date"]:
                translated_text = translate_text([extracted_text], lang_model, translation_pipeline, target_language="en")[0]

                # Custom formatting for translation
                if label == "DOB":
                    translated_text = format_dob_translation(extracted_text, translated_text)
                elif label == "Expiration date":
                    translated_text = format_expiration_translation(extracted_text, translated_text)

                output.append(f"Translated {label}: {translated_text}")

            # If label is "Expiration date", validate the year
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


def format_dob_translation(original_text, translated_text):
    """Format the DOB translation."""
    # Extract the original Japanese date
    match = re.search(r"昭和(\d{1,2})年(\d{1,2})月(\d{1,2})日", original_text)
    if match:
        year = 1926 + int(match.group(1))  # Convert Showa year to Gregorian year
        month = int(match.group(2))
        day = int(match.group(3))
        return f"Born {month}/{day}/{year}"
    return translated_text


def format_expiration_translation(original_text, translated_text):
    """Format the Expiration date translation."""
    # Extract the original Japanese expiration date
    match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", original_text)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return f"Valid until {month}/{day}/{year}"
    return translated_text


# Test the implementation
if __name__ == "__main__":
    input_file_path = r"C:\CitiDev\Japan_pipeline\data_set\japan_test_image\6f7rch30 4.png"
    result = process_dl_information(input_file_path)
    print("\n".join(result))
