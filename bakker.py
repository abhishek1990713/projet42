from ultralytics import YOLO
from PIL import Image
import os
import logging
import cv2
import pandas as pd
import re
import numpy as np
from paddleocr import PaddleOCR
from setup_log import setup_logger
from constant import (
    LOG_INIT_ERROR, LOG_PREPROCESS_ERROR, LOG_PADDING_ERROR,
    LOG_DOCTR_ERROR, LOG_PADDLE_ERROR, LOG_MRZ_ERROR, LOG_PROCESS_ERROR,
    LOG_MRZ_EXTRACTED, LOG_FIELD_EXTRACTED,
    LABEL_DOCUMENT_TYPE, LABEL_ISSUING_COUNTRY, LABEL_SURNAME, LABEL_GIVEN_NAMES,
    LABEL_PASSPORT_NUMBER, LABEL_NATIONALITY, LABEL_DATE_OF_BIRTH, LABEL_GENDER,
    LABEL_EXPIRY_DATE, GENDER_MAPPING, PADDING_LEFT, PADDING_RIGHT, PADDING_TOP,
    PADDING_BOTTOM, DOCTR_CACHE_DIR, PADDLE_DET_MODEL_DIR, PADDLE_REC_MODEL_DIR,
    PADDLE_CLS_MODEL_DIR, YOLO_MODEL_PATH, MRZ_ONE, MRZ_SECOND, UNKNOWN, INVALID_DATE
)

# Set up logger
logger = setup_logger()
logging.getLogger('ppocr').setLevel(logging.WARNING)
os.environ["DOCTR_CACHE_DIR"] = DOCTR_CACHE_DIR
os.environ["USE_TORCH"] = '2'

try:
    from doctr.models import ocr_predictor
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

    paddle_ocr = PaddleOCR(
        lang='en', use_angle_cls=False, use_gpu=False,
        det=True, rec=True, cls=False,
        det_model_dir=PADDLE_DET_MODEL_DIR,
        rec_model_dir=PADDLE_REC_MODEL_DIR,
        cls_model_dir=PADDLE_CLS_MODEL_DIR
    )
except Exception as e:
    logger.error(LOG_INIT_ERROR.format(e), exc_info=True)

def preprocess_image(image_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.error(LOG_PREPROCESS_ERROR.format(e), exc_info=True)
        return None

def add_fixed_padding(image, right=PADDING_RIGHT, left=PADDING_LEFT, top=PADDING_TOP, bottom=PADDING_BOTTOM):
    try:
        width, height = image.size
        new_width = width + right + left
        new_height = height + top + bottom
        color = (255, 255, 255) if image.mode == 'RGB' else 0
        result = Image.new(image.mode, (new_width, new_height), color)
        result.paste(image, (left, top))
        return result
    except Exception as e:
        logger.error(LOG_PADDING_ERROR.format(e), exc_info=True)
        return image

def extract_text_doctr(image_cv2):
    try:
        result_texts = ocr_model([image_cv2])
        extracted_text = ""
        if result_texts.pages:
            for page in result_texts.pages:
                for block in page.blocks:
                    for line in block.lines:
                        extracted_text += "".join([word.value for word in line.words]) + " "
        return extracted_text.strip()
    except Exception as e:
        logger.error(LOG_DOCTR_ERROR.format(e), exc_info=True)
        return ""

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
        logger.error(LOG_PADDLE_ERROR.format(e), exc_info=True)
        return ""

def format_date(yyMMdd):
    if len(yyMMdd) != 6 or not yyMMdd.isdigit():
        return INVALID_DATE
    yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
    year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
    return f"{dd}/{mm}/{year}"

def parse_mrz(mrz1, mrz2):
    try:
        mrz1 = mrz1.ljust(44, "<")[:44]
        mrz2 = mrz2.ljust(44, "<")[:44]

        document_type = mrz1[:2].strip("<")
        country_code = mrz1[2:5] if len(mrz1) > 5 else UNKNOWN

        names_part = mrz1[5:].split("<<", 1)
        surname = re.sub(r"<+", "", names_part[0]).strip() if names_part else UNKNOWN
        given_names = re.sub(r"<+", "", names_part[1]).strip() if len(names_part) > 1 else UNKNOWN

        passport_number = re.sub(r"<+$", "", mrz2[:9]) if len(mrz2) > 9 else UNKNOWN
        nationality = mrz2[10:13].strip("<") if len(mrz2) > 13 else UNKNOWN
        dob = format_date(mrz2[13:19]) if len(mrz2) > 19 else UNKNOWN
        gender_code = mrz2[20] if len(mrz2) > 20 else "X"
        gender = GENDER_MAPPING.get(gender_code, UNKNOWN)
        expiry_date = format_date(mrz2[21:27]) if len(mrz2) > 27 else UNKNOWN

        data = [
            (LABEL_DOCUMENT_TYPE, document_type),
            (LABEL_ISSUING_COUNTRY, country_code),
            (LABEL_SURNAME, surname),
            (LABEL_GIVEN_NAMES, given_names),
            (LABEL_PASSPORT_NUMBER, passport_number),
            (LABEL_NATIONALITY, nationality),
            (LABEL_DATE_OF_BIRTH, dob),
            (LABEL_GENDER, gender),
            (LABEL_EXPIRY_DATE, expiry_date)
        ]

        return pd.DataFrame(data, columns=["Label", "Extracted Text"])
    except Exception as e:
        logger.error(LOG_MRZ_ERROR.format(e), exc_info=True)
        return pd.DataFrame(columns=["Label", "Extracted Text"])

def process_passport_information(input_file_path):
    try:
        model = YOLO(YOLO_MODEL_PATH)
        input_image = preprocess_image(input_file_path)
        if input_image is None:
            raise ValueError("Failed to preprocess image")

        results = model(input_image)
        output = []
        mrz_data = {MRZ_ONE: None, MRZ_SECOND: None}

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

                if label in [MRZ_ONE, MRZ_SECOND]:
                    extracted_text = extract_text_paddle(cropped_image_cv2)
                    logger.info(LOG_MRZ_EXTRACTED.format(label, extracted_text))
                    mrz_data[label] = extracted_text
                else:
                    extracted_text = extract_text_doctr(cropped_image_cv2)
                    logger.info(LOG_FIELD_EXTRACTED.format(label, extracted_text))
                output.append({'Label': label, 'Extracted Text': extracted_text})

        if mrz_data[MRZ_ONE] and mrz_data[MRZ_SECOND]:
            mrz_df = parse_mrz(mrz_data[MRZ_ONE], mrz_data[MRZ_SECOND])
            output.extend(mrz_df.to_dict(orient="records"))

        return pd.DataFrame(output)

    except Exception as e:
        logger.error(LOG_PROCESS_ERROR.format(e), exc_info=True)
        return pd.DataFrame(columns=["Label", "Extracted Text"])



# constant.py

# Logger Messages
LOG_INIT_ERROR = "Error initializing OCR models: {}"
LOG_PREPROCESS_ERROR = "Error preprocessing image: {}"
LOG_PADDING_ERROR = "Error adding padding to image: {}"
LOG_DOCTR_ERROR = "Error extracting text using DocTR: {}"
LOG_PADDLE_ERROR = "Error extracting text using PaddleOCR: {}"
LOG_MRZ_ERROR = "Error parsing MRZ: {}"
LOG_PROCESS_ERROR = "Error processing passport information: {}"
LOG_MRZ_EXTRACTED = "Extracted MRZ {}: {}"
LOG_FIELD_EXTRACTED = "Extracted field {}: {}"

# Labels
LABEL_DOCUMENT_TYPE = "Document Type"
LABEL_ISSUING_COUNTRY = "Issuing Country"
LABEL_SURNAME = "Surname"
LABEL_GIVEN_NAMES = "Given Names"
LABEL_PASSPORT_NUMBER = "Passport Number"
LABEL_NATIONALITY = "Nationality"
LABEL_DATE_OF_BIRTH = "Date of Birth"
LABEL_GENDER = "Gender"
LABEL_EXPIRY_DATE = "Expiry Date"

# Gender Mapping
GENDER_MAPPING = {
    "M": "Male",
    "F": "Female",
    "X": "Unspecified",
    "<": "Unspecified"
}

# Padding
PADDING_RIGHT = 180
PADDING_LEFT = 100
PADDING_TOP = 100
PADDING_BOTTOM = 100

# Model Paths
DOCTR_CACHE_DIR = r"/home/ko19678/all_passport_fast_api/DocTR_models"
PADDLE_DET_MODEL_DIR = r"/home/ko19678/all_passport_fast_api/paddle_model/en_PP-OCRV3_det_infer"
PADDLE_REC_MODEL_DIR = r"/home/ko19678/all_passport_fast_api/paddle_model/en_PP-OCRv3_rec_infer"
PADDLE_CLS_MODEL_DIR = r"/home/ko19678/all_passport_fast_api/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"
YOLO_MODEL_PATH = r"/home/ko19678/all_passport_fast_api/yolo_model/best.pt"

# Field Keys
MRZ_ONE = "MRL_One"
MRZ_SECOND = "MRL_Second"

# Common Strings
UNKNOWN = "Unknown"
INVALID_DATE = "Invalid Date"
