

# Constants for model configuration
DET_ARCH = "db_resnet50"
RECO_ARCH = "crnn_vgg16_bn"

# OCR language
LANG_EN = "en"

# Image mode
MODE_RGB = "RGB"

# Padding defaults
PADDING_TOP = 100
PADDING_BOTTOM = 100
PADDING_LEFT = 100
PADDING_RIGHT = 100

# MRZ parsing
MRZ_FILL_CHAR = "<"
MRZ_LINE_LENGTH = 44
MRZ_SEPARATOR = "<<"

# Unknown fallback
UNKNOWN = "Unknown"
INVALID_DATE = "Invalid Date"

# Gender mapping
GENDER_MAPPING = {
    "M": "Male",
    "F": "Female",
    "X": "Unspecified",
    "<": "Unspecified"
}

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

# Logger messages
LOG_INIT_MODELS_ERROR = "Error initializing OCR models:"
LOG_IMAGE_PREPROCESS_ERROR = "Error preprocessing image:"
LOG_PADDING_ERROR = "Error adding padding to image:"
LOG_DOCTR_ERROR = "Error extracting text using DocTR:"
LOG_PADDLE_ERROR = "Error extracting text using PaddleOCR:"
LOG_MRZ_PARSING_ERROR = "Error parsing MRZ:"
LOG_PROCESSING_ERROR = "Error processing passport information:"
LOG_MRL_EXTRACTED = "Extracted MRZ {label}: {text}"
LOG_FIELD_EXTRACTED = "Extracted field {label}: {text}"

# Column headers
COLUMN_LABEL = "Label"
COLUMN_EXTRACTED_TEXT = "Extracted Text"

# OCR model paths
DOCTR_CACHE_DIR = "/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models/models/models"
PADDLE_DET_MODEL_DIR = "/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
PADDLE_REC_MODEL_DIR = "/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
PADDLE_CLS_MODEL_DIR = "/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"
YOLO_MODEL_PATH = "/home/ko19678/japan_pipeline/ALL_Passport/best.pt"

# Label identifiers for MRZ
LABEL_MRL_ONE = "MRL_One"
LABEL_MRL_SECOND = "MRL_Second"



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
import constant as const

# Set up logger
logger = setup_logger()

# Reduce PaddleOCR log level
logging.getLogger('ppocr').setLevel(logging.WARNING)

# Environment setup
os.environ[const.DOCTR_CACHE_VAR] = const.DOCTR_CACHE_PATH
os.environ[const.USE_TORCH_VAR] = const.USE_TORCH_VAL

try:
    # Initialize OCR models with specific architectures and paths
    ocr_model = ocr_predictor(
        det_arch=const.DOCTR_DET_ARCH,
        reco_arch=const.DOCTR_RECO_ARCH,
        pretrained=True
    )

    det_model_dir = const.PADDLE_DET_MODEL_DIR
    rec_model_dir = const.PADDLE_REC_MODEL_DIR
    cls_model_dir = const.PADDLE_CLS_MODEL_DIR

    paddle_ocr = PaddleOCR(
        lang=const.LANGUAGE,
        use_angle_cls=False,
        use_gpu=False,
        det=True,
        rec=True,
        cls=False,
        det_model_dir=det_model_dir,
        rec_model_dir=rec_model_dir,
        cls_model_dir=cls_model_dir
    )

    passport_model_path = const.PASSPORT_MODEL_PATH

except Exception as e:
    logger.error(const.ERROR_INITIALIZING_OCR_MODELS.format(str(e)), exc_info=True)


def preprocess_image(image_path):
    """This function loads an image and converts it to RGB mode if it's not already."""
    try:
        image = Image.open(image_path)
        if image.mode != const.RGB_MODE:
            image = image.convert(const.RGB_MODE)
        return image
    except Exception as e:
        logger.error(const.ERROR_PREPROCESS_IMAGE.format(str(e)), exc_info=True)
        return None


def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    """Adds fixed white padding to the image on all sides."""
    try:
        width, height = image.size
        new_width = width + right + left
        new_height = height + top + bottom
        color = (255, 255, 255) if image.mode == const.RGB_MODE else 0
        result = Image.new(image.mode, (new_width, new_height), color)
        result.paste(image, (left, top))
        return result
    except Exception as e:
        logger.error(const.ERROR_PADDING_IMAGE.format(str(e)), exc_info=True)
        return image


def extract_text_doctr(image_cv2):
    """Extracts text from an image using DocTR OCR model."""
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
        logger.error(const.ERROR_DOCTR_TEXT.format(str(e)), exc_info=True)
        return ""


def extract_text_paddle(image_cv2):
    """Extracts text from an image using PaddleOCR model."""
    try:
        result_texts = paddle_ocr.ocr(image_cv2, cls=False)
        extracted_text = ""
        if result_texts:
            for result in result_texts:
                for line in result:
                    extracted_text += line[1][0] + " "
        return extracted_text.strip()
    except Exception as e:
        logger.error(const.ERROR_PADDLE_TEXT.format(str(e)), exc_info=True)
        return ""


def parse_mrz(mrl1, mrl2):
    """Parses two MRZ lines from a passport and extracts structured information."""
    try:
        mrl1 = mrl1.ljust(44, const.FILLER_CHAR)[:44]
        mrl2 = mrl2.ljust(44, const.FILLER_CHAR)[:44]

        document_type = mrl1[:2].strip(const.FILLER_CHAR)
        country_code = mrl1[2:5] if len(mrl1) > 5 else const.UNKNOWN
        names_part = mrl1[5:].split(const.NAME_SEPARATOR, 1)
        surname = re.sub(const.LESS_THAN_REGEX, const.EMPTY_STRING, names_part[0]).strip() if names_part else const.UNKNOWN
        given_names = re.sub(const.LESS_THAN_REGEX, const.EMPTY_STRING, names_part[1]).strip() if len(names_part) > 1 else const.UNKNOWN
        passport_number = re.sub(const.TRAILING_LESS_THAN_REGEX, const.EMPTY_STRING, mrl2[:9]) if len(mrl2) > 9 else const.UNKNOWN
        nationality = mrl2[10:13].strip(const.FILLER_CHAR) if len(mrl2) > 13 else const.UNKNOWN

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
        gender = gender_mapping.get(gender_code, const.GENDER_UNSPECIFIED)

        data = [
            (const.DOC_TYPE_LABEL, document_type),
            (const.COUNTRY_LABEL, country_code),
            (const.SURNAME_LABEL, surname),
            (const.GIVEN_LABEL, given_names),
            (const.PASSPORT_LABEL, passport_number),
            (const.NATIONALITY_LABEL, nationality),
            (const.DOB_LABEL, dob),
            (const.GENDER_LABEL, gender),
            (const.EXPIRY_LABEL, expiry_date),
        ]

        return pd.DataFrame(data, columns=const.DATAFRAME_COLUMNS)
    except Exception as e:
        logger.error(const.ERROR_PARSING_MRZ.format(str(e)), exc_info=True)
        return pd.DataFrame(columns=const.DATAFRAME_COLUMNS)


def process_passport_information(input_file_path):
    """Processes a passport image and extracts structured information using YOLO + OCR."""
    try:
        model = YOLO(passport_model_path)
        input_image = preprocess_image(input_file_path)
        if input_image is None:
            raise ValueError(const.ERROR_PREPROCESS_FAILED)

        results = model(input_image)
        output = []
        mrz_data = {const.MRL_ONE: None, const.MRL_SECOND: None}

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

                if label in [const.MRL_ONE, const.MRL_SECOND]:
                    extracted_text = extract_text_paddle(cropped_image_cv2)
                    logger.info(const.INFO_EXTRACTED_MRZ.format(label, extracted_text))
                    mrz_data[label] = extracted_text
                else:
                    extracted_text = extract_text_doctr(cropped_image_cv2)
                    logger.info(const.INFO_EXTRACTED_FIELD.format(label, extracted_text))
                    output.append({const.LABEL_KEY: label, const.TEXT_KEY: extracted_text})

        if mrz_data[const.MRL_ONE] and mrz_data[const.MRL_SECOND]:
            mrz_df = parse_mrz(mrz_data[const.MRL_ONE], mrz_data[const.MRL_SECOND])
            output.extend(mrz_df.to_dict(orient=const.DICT_ORIENT))

        return pd.DataFrame(output)
    except Exception as e:
        logger.error(const.ERROR_PROCESSING_PASSPORT.format(str(e)), exc_info=True)
        return pd.DataFrame(columns=const.DATAFRAME_COLUMNS)
