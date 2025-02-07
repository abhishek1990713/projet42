i
import os
import cv2
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
from doctr.models import ocr_predictor
from ultralytics import YOLO

# Setup logging
logging.getLogger('ppocr').setLevel(logging.WARNING)

# DocTR configuration
os.environ["DOCTR_CACHE_DIR"] = r"/home/ko19678/japan_pipeline/japan_pipeline/DocTR_Models"
os.environ['USE_TORCH'] = '1'

# Initialize DocTR OCR model
ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

# All model paths and constants
passport_model_path = "/path/to/your/passport_model.pt"
valid_issue_date = datetime.strptime("01 Jan 2000", "%d %b %Y")
valid_expiry_date = datetime.strptime("31 Dec 2030", "%d %b %Y")


def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(image.mode, (new_width, new_height), (0, 0, 255))
    result.paste(image, (left, top))
    return result


def process_passport_information(input_file_path):
    model = YOLO(passport_model_path)
    results = model(input_file_path)
    input_image = Image.open(input_file_path)

    output_data = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            bbox = box.xyxy.tolist()[0]

            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            padded_image = add_fixed_padding(cropped_image)
            cropped_image_np = np.array(padded_image)
            cropped_image_cv2 = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

            result_texts = ocr_model([cropped_image_cv2])
            extracted_text = ""

            if result_texts.pages:
                for page in result_texts.pages:
                    for block in page.blocks:
                        for line in block.lines:
                            extracted_text += " ".join([word.value for word in line.words]) + " "
            extracted_text = extracted_text.strip()

            output_data.append({'Label': label, 'Extracted_text': extracted_text})

    # Convert to DataFrame
    data = pd.DataFrame(output_data)

    # Check extracted dates
    date_of_issue = None
    date_of_expiry = None

    for index, row in data.iterrows():
        if row['Label'] == "Date of issue":
            try:
                date_of_issue = datetime.strptime(row['Extracted_text'], "%d %b %Y")
                data.loc[index, 'Extracted_text'] = date_of_issue
            except ValueError:
                logging.warning(f"Could not parse Date of Issue: {row['Extracted_text']}")
        elif row['Label'] == "Date of expiry":
            try:
                date_of_expiry = datetime.strptime(row['Extracted_text'], "%d %b %Y")
                data.loc[index, 'Extracted_text'] = date_of_expiry
            except ValueError:
                logging.warning(f"Could not parse Date of Expiry: {row['Extracted_text']}")

    # Validate dates
    if date_of_issue and date_of_expiry:
        if valid_issue_date <= date_of_issue <= valid_expiry_date and date_of_expiry <= valid_expiry_date:
            validation_message = "Passport is valid within the given date range."
        else:
            validation_message = "Passport dates do not fall within the valid range."
    else:
        validation_message = "One or both dates could not be extracted or are invalid."

    # Add validation message to DataFrame
    data = pd.concat([data, pd.DataFrame([{'Label': 'Validation', 'Extracted_text': validation_message}])])

    return data

