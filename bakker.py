

# mrl_passport.py
from PIL import Image
import os
import numpy as np
import logging
import cv2
import pandas as pd
import re
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from logger_config import setup_logger

logger = setup_logger("mrl_passport", "passport.log")

os.environ["DOCTR_CACHE_DIR"] = r"/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models/models/models"
os.environ['USE_TORCH'] = '1'

try:
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
except Exception as e:
    logger.error(f"Failed to load doctr model: {e}")
    raise

det_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
rec_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
cls_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"

try:
    paddle_ocr = PaddleOCR(lang='en', use_angle_cls=False, use_gpu=False, det=True, rec=True,
                           cls=False, det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
                           cls_model_dir=cls_model_dir)
except Exception as e:
    logger.error(f"Failed to load paddleocr model: {e}")
    raise

passport_model_path = r"/home/ko19678/japan_pipeline/ALL_Passport/best.pt"


def preprocess_image(image_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.error(f"Error in preprocess_image: {e}")
        raise


def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    try:
        width, height = image.size
        new_width = width + right + left
        new_height = height + top + bottom
        color = (255, 255, 255) if image.mode == 'RGB' else 255
        result = Image.new(image.mode, (new_width, new_height), color)
        result.paste(image, (left, top))
        return result
    except Exception as e:
        logger.error(f"Error in add_fixed_padding: {e}")
        raise


def extract_text_doctr(image_cv2):
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
        logger.error(f"Error in extract_text_doctr: {e}")
        raise


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
        logger.error(f"PaddleOCR extraction failed: {e}")
        raise


def parse_mrz(mrl1, mrl2):
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
        return df
    except Exception as e:
        logger.error(f"Error in parse_mrz: {e}")
        raise
