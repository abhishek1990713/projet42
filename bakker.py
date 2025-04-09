# constant.py

# Log Messages
ERROR_INITIALIZING_OCR = "Error initializing OCR models: {}"
ERROR_PREPROCESSING_IMAGE = "Error preprocessing image: {}"
ERROR_PADDING_IMAGE = "Error adding padding to image: {}"
ERROR_TEXT_DOCTR = "Error extracting text using DocTR: {}"
ERROR_TEXT_PADDLE = "Error extracting text using PaddleOCR: {}"
ERROR_PARSING_MRZ = "Error parsing MRZ: {}"
ERROR_PROCESSING_PASSPORT = "Error processing passport information: {}"
FAILED_PREPROCESS_IMAGE = "Failed to preprocess image"
LOG_EXTRACTED_MRL = "Extracted MRZ {}: {}"
LOG_EXTRACTED_FIELD = "Extracted field {}: {}"

# Labels
LABEL_DOCUMENT_TYPE = "Document Type"
LABEL_COUNTRY = "Issuing Country"
LABEL_SURNAME = "Surname"
LABEL_GIVEN_NAMES = "Given Names"
LABEL_PASSPORT_NUMBER = "Passport Number"
LABEL_NATIONALITY = "Nationality"
LABEL_DOB = "Date of Birth"
LABEL_GENDER = "Gender"
LABEL_EXPIRY = "Expiry Date"

# MRZ Keys
MRL_ONE = "MRL_One"
MRL_SECOND = "MRL_Second"

# Gender Map
GENDER_MAPPING = {
    "M": "Male",
    "F": "Female",
    "X": "Unspecified",
    "<": "Unspecified"
}

# Misc
UNKNOWN = "Unknown"
INVALID_DATE = "Invalid Date"
UNSPECIFIED = "Unspecified"

# Model Paths
DOCTR_CACHE_DIR = "/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models/models/models"
PASSPORT_MODEL_PATH = "/home/ko19678/japan_pipeline/ALL_Passport/best.pt"
PADDLE_DET_MODEL = "/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
PADDLE_REC_MODEL = "/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
PADDLE_CLS_MODEL = "/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"



from ultralytics import YOLO
from PIL import Image
import os
import numpy as np
import logging
import cv2
import pandas as pd
import re
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from setup import setup_logger
from mrz_mrl import parse_mrz_mrl
from constant import (
    ERROR_INITIALIZING_OCR, ERROR_PREPROCESSING_IMAGE, ERROR_PADDING_IMAGE,
    ERROR_TEXT_DOCTR, ERROR_TEXT_PADDLE, ERROR_PARSING_MRZ,
    ERROR_PROCESSING_PASSPORT, FAILED_PREPROCESS_IMAGE,
    LOG_EXTRACTED_MRL, LOG_EXTRACTED_FIELD,
    LABEL_DOCUMENT_TYPE, LABEL_COUNTRY, LABEL_SURNAME,
    LABEL_GIVEN_NAMES, LABEL_PASSPORT_NUMBER, LABEL_NATIONALITY,
    LABEL_DOB, LABEL_GENDER, LABEL_EXPIRY,
    MRL_ONE, MRL_SECOND, GENDER_MAPPING, UNKNOWN, INVALID_DATE,
    DOCTR_CACHE_DIR, PASSPORT_MODEL_PATH,
    PADDLE_DET_MODEL, PADDLE_REC_MODEL, PADDLE_CLS_MODEL
)

# Set up logger
logger = setup_logger()

# Reduce PaddleOCR log level
logging.getLogger('ppocr').setLevel(logging.WARNING)

# Environment setup
os.environ["DOCTR_CACHE_DIR"] = DOCTR_CACHE_DIR
os.environ["USE_TORCH"] = '1'

try:
    ocr_model = ocr_predictor(
        det_arch='db_resnet50',
        reco_arch='crnn_vgg16_bn',
        pretrained=True
    )

    paddle_ocr = PaddleOCR(
        lang='en',
        use_angle_cls=False,
        use_gpu=False,
        det=True,
        rec=True,
        cls=False,
        det_model_dir=PADDLE_DET_MODEL,
        rec_model_dir=PADDLE_REC_MODEL,
        cls_model_dir=PADDLE_CLS_MODEL
    )

except Exception as e:
    logger.error(ERROR_INITIALIZING_OCR.format(e), exc_info=True)


def preprocess_image(image_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.error(ERROR_PREPROCESSING_IMAGE.format(e), exc_info=True)
        return None


def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    try:
        width, height = image.size
        new_width = width + right + left
        new_height = height + top + bottom
        color = (255, 255, 255) if image.mode == 'RGB' else 0
        result = Image.new(image.mode, (new_width, new_height), color)
        result.paste(image, (left, top))
        return result
    except Exception as e:
        logger.error(ERROR_PADDING_IMAGE.format(e), exc_info=True)
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
        logger.error(ERROR_TEXT_DOCTR.format(e), exc_info=True)
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
        logger.error(ERROR_TEXT_PADDLE.format(e), exc_info=True)
        return ""


def parse_mrz(mrl1, mrl2):
    try:
        mrl1 = mrl1.ljust(44, "<")[:44]
        mrl2 = mrl2.ljust(44, "<")[:44]

        document_type = mrl1[:2].strip("<")
        country_code = mrl1[2:5] if len(mrl1) > 5 else UNKNOWN
        names_part = mrl1[5:].split("<<", 1)
        surname = re.sub(r"<+", "", names_part[0]).strip() if names_part else UNKNOWN
        given_names = re.sub(r"<+", "", names_part[1]).strip() if len(names_part) > 1 else UNKNOWN
        passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) > 9 else UNKNOWN
        nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else UNKNOWN

        def format_date(yyMMdd):
            if len(yyMMdd) != 6 or not yyMMdd.isdigit():
                return INVALID_DATE
            yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
            year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
            return f"{dd}/{mm}/{year}"

        dob = format_date(mrl2[13:19]) if len(mrl2) > 19 else UNKNOWN
        expiry_date = format_date(mrl2[21:27]) if len(mrl2) > 27 else UNKNOWN
        gender_code = mrl2[20] if len(mrl2) > 20 else "X"
        gender = GENDER_MAPPING.get(gender_code, UNSPECIFIED)

        data = [
            (LABEL_DOCUMENT_TYPE, document_type),
            (LABEL_COUNTRY, country_code),
            (LABEL_SURNAME, surname),
            (LABEL_GIVEN_NAMES, given_names),
            (LABEL_PASSPORT_NUMBER, passport_number),
            (LABEL_NATIONALITY, nationality),
            (LABEL_DOB, dob),
            (LABEL_GENDER, gender),
            (LABEL_EXPIRY, expiry_date),
        ]

        return pd.DataFrame(data, columns=["Label", "Extracted Text"])
    except Exception as e:
        logger.error(ERROR_PARSING_MRZ.format(e), exc_info=True)
        return pd.DataFrame(columns=["Label", "Extracted Text"])


def process_passport_information(input_file_path):
    try:
        model = YOLO(PASSPORT_MODEL_PATH)
        input_image = preprocess_image(input_file_path)
        if input_image is None:
            raise ValueError(FAILED_PREPROCESS_IMAGE)

        results = model(input_image)
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

                if label in [MRL_ONE, MRL_SECOND]:
                    extracted_text = extract_text_paddle(cropped_image_cv2)
                    logger.info(LOG_EXTRACTED_MRL.format(label, extracted_text))
                    mrz_data[label] = extracted_text
                else:
                    extracted_text = extract_text_doctr(cropped_image_cv2)
                    logger.info(LOG_EXTRACTED_FIELD.format(label, extracted_text))
                    output.append({'Label': label, 'Extracted Text': extracted_text})

        if mrz_data[MRL_ONE] and mrz_data[MRL_SECOND]:
            mrz_df = parse_mrz(mrz_data[MRL_ONE], mrz_data[MRL_SECOND])
            output.extend(mrz_df.to_dict(orient="records"))

        return pd.DataFrame(output)
    except Exception as e:
        logger.error(ERROR_PROCESSING_PASSPORT.format(e), exc_info=True)
        return pd.DataFrame(columns=["Label", "Extracted Text"])

