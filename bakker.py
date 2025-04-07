9# mrl_passport.py
from PIL # logger_config.py
import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = "passport.log"):
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)
    
    log_path = os.path.join(log_directory, log_file)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# mrl_passport.py
from PIL import Image
import os
import numpy as np
import cv2
import pandas as pd
import re
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from logger_config import setup_logger

logger = setup_logger("passport_logger", "passport.log")

os.environ["DOCTR_CACHE_DIR"] = r"/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models/models/models"
os.environ['USE_TORCH'] = '1'

try:
    logger.info("Loading Doctr OCR model")
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    logger.info("Doctr OCR model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Doctr model: {e}")
    raise

det_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
rec_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
cls_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"

try:
    logger.info("Loading PaddleOCR model")
    paddle_ocr = PaddleOCR(lang='en', use_angle_cls=False, use_gpu=False, det=True, rec=True,
                           cls=False, det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
                           cls_model_dir=cls_model_dir)
    logger.info("PaddleOCR model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load PaddleOCR model: {e}")
    raise

passport_model_path = r"/home/ko19678/japan_pipeline/ALL_Passport/best.pt"

def preprocess_image(image_path):
    logger.info(f"Preprocessing image: {image_path}")
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.exception("Error in preprocess_image")
        raise

def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    logger.info("Adding fixed padding to image")
    try:
        width, height = image.size
        new_width = width + right + left
        new_height = height + top + bottom
        color = (255, 255, 255) if image.mode == 'RGB' else 255
        result = Image.new(image.mode, (new_width, new_height), color)
        result.paste(image, (left, top))
        return result
    except Exception as e:
        logger.exception("Error in add_fixed_padding")
        raise

def extract_text_doctr(image_cv2):
    logger.info("Extracting text using Doctr")
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
        logger.exception("Error in extract_text_doctr")
        raise

def extract_text_paddle(image_cv2):
    logger.info("Extracting text using PaddleOCR")
    try:
        result_texts = paddle_ocr.ocr(image_cv2, cls=False)
        extracted_text = ""
        if result_texts:
            for result in result_texts:
                for line in result:
                    extracted_text += line[1][0] + " "
        return extracted_text.strip()
    except Exception as e:
        logger.exception("PaddleOCR extraction failed")
        raise

def parse_mrz(mrl1, mrl2):
    logger.info("Parsing MRZ lines")
    try:
        mrl1 = mrl1.ljust(44, "<")[:44]
        mrl2 = mrl2.ljust(44, "<")[:44]

        document_type = mrl1[:2].strip("<")
        country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"
        names_part = mrl1[5:].split("<<", 1)
        surname = re.sub(r"<+", "", names_part[0]).strip() if names_part else "Unknown"
        given_names = re.sub(r"<+", "", names_part[1]).strip() if len(names_part) > 1 else "Unknown"
        passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) > 9 else "Unknown"
        nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else "Unknown"

        def format_date(yyMMdd):
            if len(yyMMdd) != 6 or not yyMMdd.isdigit():
                return "Invalid Date"
            yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
            year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
            return f"{dd}/{mm}/{year}"

        dob = format_date(mrl2[13:19]) if len(mrl2) > 19 else "Unknown"
        expiry_date = format_date(mrl2[21:27]) if len(mrl2) > 27 else "Unknown"
        gender_code = mrl2[20] if len(mrl2) > 20 else "X"
        gender_mapping = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}
        gender = gender_mapping.get(gender_code, "Unspecified")
        optional_data = re.sub(r"<+$", "", mrl2[28:]).strip() if len(mrl2) > 28 else "N/A"

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
        ]

        df = pd.DataFrame(data, columns=["Label", "Extracted Text"])
        logger.info("MRZ parsed successfully")
        return df
    except Exception as e:
        logger.exception("Error in parse_mrz")
        raise
: 
