# Paths
PASSPORT_MODEL_PATH = "path_to_yolo_passport_model.pt"
DOCTR_CACHE_DIR = "/tmp/doctr"
DET_MODEL_DIR = "path_to_paddle_det_model"
REC_MODEL_DIR = "path_to_paddle_rec_model"
CLS_MODEL_DIR = "path_to_paddle_cls_model"
PASSPORT_LOG_FILE = "logs/passport.log"

# Modes
RGB_MODE = "RGB"

# Logging Messages
LOADING_DOCTR = "Loading Doctr OCR model..."
DOCTR_LOADED = "Doctr OCR model loaded successfully."
DOCTR_LOAD_FAILED = "Failed to load Doctr OCR model."

LOADING_PADDLE = "Loading PaddleOCR model..."
PADDLE_LOADED = "PaddleOCR model loaded successfully."
PADDLE_LOAD_FAILED = "Failed to load PaddleOCR model."

PREPROCESSING_IMAGE = "Preprocessing image"
PREPROCESS_IMAGE_ERROR = "Error in preprocess_image function."

ADDING_PADDING = "Adding fixed padding to the image."
PADDING_ERROR = "Error in add_fixed_padding function."

EXTRACTING_DOCTR = "Extracting text using Doctr OCR..."
DOCTR_EXTRACTION_ERROR = "Error in extract_text_doctr function."

EXTRACTING_PADDLE = "Extracting text using PaddleOCR..."
PADDLE_EXTRACTION_ERROR = "Error in extract_text_paddle function."

PARSING_MRZ = "Parsing MRZ lines..."
MRZ_PARSED = "MRZ parsed successfully."
MRZ_PARSE_ERROR = "Error parsing MRZ lines."

# Text Defaults
UNKNOWN = "Unknown"
NA = "N/A"
INVALID_DATE = "Invalid Date"
UNSPECIFIED = "Unspecified"

# Gender Mapping
GENDER_MAPPING = {
    'M': 'Male',
    'F': 'Female',
    '<': 'Unspecified',
    'X': 'Unspecified'
}

# Labels
LABEL_DOCUMENT_TYPE = "Document Type"
LABEL_ISSUING_COUNTRY = "Issuing Country"
LABEL_SURNAME = "Surname"
LABEL_GIVEN_NAMES = "Given Names"
LABEL_PASSPORT_NUMBER = "Passport Number"
LABEL_NATIONALITY = "Nationality"
LABEL_DOB = "Date of Birth"
LABEL_GENDER = "Gender"
LABEL_EXPIRY_DATE = "Date of Expiry"
LABEL_COL = "Field"
TEXT_COL = "Value"




import logging
import os
from datetime import datetime
from PIL import Image
import numpy as np
import cv2
import pandas as pd
import re
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from logger_config import setup_logger
import constant as const

logger = setup_logger("passport_logger", const.PASSPORT_LOG_FILE)

# Environment Variables
os.environ["DOCTR_CACHE_DIR"] = const.DOCTR_CACHE_DIR
os.environ['USE_TORCH'] = '1'

# Load Doctr OCR
try:
    logger.info(const.LOADING_DOCTR)
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    logger.info(const.DOCTR_LOADED)
except Exception as e:
    logger.error(f"{const.DOCTR_LOAD_FAILED} {e}")
    raise

# Load PaddleOCR
try:
    logger.info(const.LOADING_PADDLE)
    paddle_ocr = PaddleOCR(lang='en', use_angle_cls=False, use_gpu=False, det=True, rec=True,
                           cls=False, det_model_dir=const.DET_MODEL_DIR, 
                           rec_model_dir=const.REC_MODEL_DIR,
                           cls_model_dir=const.CLS_MODEL_DIR)
    logger.info(const.PADDLE_LOADED)
except Exception as e:
    logger.error(f"{const.PADDLE_LOAD_FAILED} {e}")
    raise

passport_model_path = const.PASSPORT_MODEL_PATH

def preprocess_image(image_path):
    logger.info(f"{const.PREPROCESSING_IMAGE}: {image_path}")
    try:
        image = Image.open(image_path)
        if image.mode != const.RGB_MODE:
            image = image.convert(const.RGB_MODE)
        return image
    except Exception as e:
        logger.exception(const.PREPROCESS_IMAGE_ERROR)
        raise

def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    logger.info(const.ADDING_PADDING)
    try:
        width, height = image.size
        new_width = width + right + left
        new_height = height + top + bottom
        color = (255, 255, 255) if image.mode == const.RGB_MODE else 255
        result = Image.new(image.mode, (new_width, new_height), color)
        result.paste(image, (left, top))
        return result
    except Exception as e:
        logger.exception(const.PADDING_ERROR)
        raise

def extract_text_doctr(image_cv2):
    logger.info(const.EXTRACTING_DOCTR)
    try:
        result_texts = ocr_model([image_cv2])
        extracted_text = ""
        if result_texts.pages:
            for page in result_texts.pages:
                for block in page.blocks:
                    for line in block.lines:
                        extracted_text += " ".join([word.value for word in line.words]) + " "
        return extracted_text.strip()
    except Exception as e:
        logger.exception(const.DOCTR_EXTRACTION_ERROR)
        raise

def extract_text_paddle(image_cv2):
    logger.info(const.EXTRACTING_PADDLE)
    try:
        result_texts = paddle_ocr.ocr(image_cv2, cls=False)
        extracted_text = ""
        if result_texts:
            for result in result_texts:
                for line in result:
                    extracted_text += line[1][0] + " "
        return extracted_text.strip()
    except Exception as e:
        logger.exception(const.PADDLE_EXTRACTION_ERROR)
        raise

def parse_mrz(mrl1, mrl2):
    logger.info(const.PARSING_MRZ)
    try:
        mrl1 = mrl1.ljust(44, "<")[:44]
        mrl2 = mrl2.ljust(44, "<")[:44]

        document_type = mrl1[:2].strip("<")
        country_code = mrl1[2:5] if len(mrl1) > 5 else const.UNKNOWN
        names_part = mrl1[5:].split("<<", 1)
        surname = re.sub(r"<+", "", names_part[0]).strip() if names_part else const.UNKNOWN
        given_names = re.sub(r"<+", "", names_part[1]).strip() if len(names_part) > 1 else const.UNKNOWN
        passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) > 9 else const.UNKNOWN
        nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else const.UNKNOWN

        def format_date(yyMMdd):
            if len(yyMMdd) != 6 or not yyMMdd.isdigit():
                return const.INVALID_DATE
            yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
            year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
            return f"{dd}/{mm}/{year}"

        dob = format_date(mrl2[13:19]) if len(mrl2) > 19 else const.UNKNOWN
        expiry_date = format_date(mrl2[21:27]) if len(mrl2) > 27 else const.UNKNOWN
        gender_code = mrl2[20] if len(mrl2) > 20 else "X"
        gender_mapping = const.GENDER_MAPPING
        gender = gender_mapping.get(gender_code, const.UNSPECIFIED)
        optional_data = re.sub(r"<+$", "", mrl2[28:]).strip() if len(mrl2) > 28 else const.NA

        data = [
            (const.LABEL_DOCUMENT_TYPE, document_type),
            (const.LABEL_ISSUING_COUNTRY, country_code),
            (const.LABEL_SURNAME, surname),
            (const.LABEL_GIVEN_NAMES, given_names),
            (const.LABEL_PASSPORT_NUMBER, passport_number),
            (const.LABEL_NATIONALITY, nationality),
            (const.LABEL_DOB, dob),
            (const.LABEL_GENDER, gender),
            (const.LABEL_EXPIRY_DATE, expiry_date),
        ]

        df = pd.DataFrame(data, columns=[const.LABEL_COL, const.TEXT_COL])
        logger.info(const.MRZ_PARSED)
        return df
    except Exception as e:
        logger.exception(const.MRZ_PARSE_ERROR)
        raise


import logging
import os
from constant import PASSPORT_LOG_FILE

def setup_logger(name: str):
    log_path = PASSPORT_LOG_FILE
    log_directory = os.path.dirname(log_path)
    os.makedirs(log_directory, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
