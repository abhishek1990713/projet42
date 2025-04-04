

from ultralytics import YOLO
from PIL import Image
import os
import numpy as np
import cv2
import pandas as pd
import re
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from logger_config import logger
from constant import *

# Set PaddleOCR logging
logging.getLogger(LOG_PPOCR_LEVEL).setLevel(LOGGING_LEVEL)

# Set environment variables
os.environ["DOCTR_CACHE_DIR"] = DOCTR_CACHE_DIR
os.environ['USE_TORCH'] = '1'

ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

paddle_ocr = PaddleOCR(
    lang='en',
    use_angle_cls=False,
    use_gpu=False,
    det=True,
    rec=True,
    cls=False,
    det_model_dir=DET_MODEL_DIR,
    rec_model_dir=REC_MODEL_DIR,
    cls_model_dir=CLS_MODEL_DIR
)

def preprocess_image(image_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise

def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom
    color = (255, 255, 255)
    result = Image.new(image.mode, (new_width, new_height), color)
    result.paste(image, (left, top))
    return result

def extract_text_paddle(image_cv2):
    try:
        result_texts = paddle_ocr.ocr(image_cv2, cls=False)
        extracted_text = ""
        if result_texts:
            for result in result_texts:
                for line in result:
                    extracted_text += line[1][0] + " "
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"PaddleOCR extraction error: {e}")
        raise

def parse_mrz(mrz1, mrz2):
    try:
        mrz1 = mrz1.ljust(44, "<")[:44]
        mrz2 = mrz2.ljust(44, "<")[:44]

        document_type = mrz1[:2].strip("<")
        country_code = mrz1[2:5]
        names_part = mrz1[5:].split("<<", 1)
        surname = re.sub(r"<+", "", names_part[0]).strip()
        given_names = re.sub(r"<+", "", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

        passport_number = re.sub(r"<+$", "", mrz2[:9])
        nationality = mrz2[10:13].strip("<")

        def format_date(yyMMdd):
            if len(yyMMdd) != 6 or not yyMMdd.isdigit():
                return "Invalid Date"
            yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
            year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
            return f"{dd}/{mm}/{year}"

        dob = format_date(mrz2[13:19])
        expiry_date = format_date(mrz2[21:27])
        gender_code = mrz2[20]
        gender = GENDER_MAPPING.get(gender_code, "Unspecified")
        optional_data = re.sub(r"<+$", "", mrz2[28:]).strip()

        data = [
            ("Document Type", document_type),
            ("Issuing Country", country_code),
            ("Surname", surname),
            ("Given Names", given_names),
            ("Passport Number", passport_number),
            ("Nationality", nationality),
            ("Date of Birth", dob),
            ("Gender", gender),
            ("Expiry Date", expiry_date),
            ("Optional Data", optional_data)
        ]
        return pd.DataFrame(data, columns=["Label", "Extracted Text"])
    except Exception as e:
        logger.error(f"Error parsing MRZ: {e}")
        raise

def process_passport_information(input_file_path):
    try:
        model = YOLO(PASSPORT_MODEL_PATH)
        input_image = preprocess_image(input_file_path)
        results = model(input_image)
        input_image = Image.open(input_file_path)

        output = []
        mrz_data = {MRL_ONE: None, MRL_SECOND: None}

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

                extracted_text = extract_text_paddle(cropped_image_cv2)

                if label in [MRL_ONE, MRL_SECOND]:
                    mrz_data[label] = extracted_text
                else:
                    output.append({'Label': label, 'Extracted Text': extracted_text})

        if mrz_data[MRL_ONE] and mrz_data[MRL_SECOND]:
            mrz_df = parse_mrz(mrz_data[MRL_ONE], mrz_data[MRL_SECOND])
            output.extend(mrz_df.to_dict(orient="records"))

        return pd.DataFrame(output)
    except Exception as e:
        logger.error(f"Error processing passport information: {e}")
        raise

