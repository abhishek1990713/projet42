

import os
import cv2
import numpy as np
import pandas as pd
import re
from PIL import Image
from ultralytics import YOLO
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor

from logger_config import logger
from constant import (
    DOCTR_CACHE_DIR, USE_TORCH,
    DET_MODEL_DIR, REC_MODEL_DIR, CLS_MODEL_DIR,
    MRL_MODEL_PATH, LANG,
    INVALID_IMAGE_MODE, EXTRACT_DOCTR_LOG, EXTRACT_PADDLE_LOG,
    PARSE_MRZ_LOG, PROCESS_START_LOG, PROCESS_COMPLETE_LOG,
    PARSE_EXCEPTION_LOG, PROCESS_EXCEPTION_LOG
)

# Configure environment
os.environ["DOCTR_CACHE_DIR"] = DOCTR_CACHE_DIR
os.environ["USE_TORCH"] = USE_TORCH

# Load models
ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
paddle_ocr = PaddleOCR(
    lang=LANG,
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
            logger.warning(INVALID_IMAGE_MODE)
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.exception(f"Error in preprocess_image: {e}")
        raise

def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom
    color = (255, 255, 255) if image.mode == 'RGB' else 0
    result = Image.new(image.mode, (new_width, new_height), color)
    result.paste(image, (left, top))
    return result

def extract_text_doctr(image_cv2):
    try:
        logger.debug(EXTRACT_DOCTR_LOG)
        result = ocr_model([image_cv2])
        extracted_text = ""
        if result.pages:
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        extracted_text += " ".join([word.value for word in line.words]) + " "
        return extracted_text.strip()
    except Exception as e:
        logger.exception(f"Error in extract_text_doctr: {e}")
        return ""

def extract_text_paddle(image_cv2):
    try:
        logger.debug(EXTRACT_PADDLE_LOG)
        result = paddle_ocr.ocr(image_cv2, cls=False)
        extracted_text = ""
        if result:
            for line_group in result:
                for line in line_group:
                    extracted_text += line[1][0] + " "
        return extracted_text.strip()
    except Exception as e:
        logger.exception(f"Error in extract_text_paddle: {e}")
        return ""

def parse_mrz(mrl1, mrl2):
    try:
        logger.debug(PARSE_MRZ_LOG)
        mrl1 = mrl1.ljust(44, "<")[:44]
        mrl2 = mrl2.ljust(44, "<")[:44]

        document_type = mrl1[:2].strip("<")
        country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"
        names_part = mrl1[5:].split("<<", 1)
        surname = re.sub(r"<+", " ", names_part[0]).strip() if names_part else "Unknown"
        given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

        passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) > 9 else "Unknown"
        nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else "Unknown"

        def format_date(ymd):
            if len(ymd) != 6 or not ymd.isdigit():
                return "Invalid Date"
            yy, mm, dd = ymd[:2], ymd[2:4], ymd[4:6]
            year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
            return f"{dd}/{mm}/{year}"

        dob = format_date(mrl2[13:19]) if len(mrl2) > 19 else "Unknown"
        gender_code = mrl2[20] if len(mrl2) > 20 else "X"
        gender_map = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}
        gender = gender_map.get(gender_code, "Unspecified")
        expiry_date = format_date(mrl2[21:27]) if len(mrl2) > 27 else "Unknown"
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
            ("Optional Data", optional_data)
        ]

        return pd.DataFrame(data, columns=["Label", "Extracted Text"])
    except Exception as e:
        logger.exception(PARSE_EXCEPTION_LOG)
        return pd.DataFrame(columns=["Label", "Extracted Text"])

def process_passport_information(image_path):
    try:
        logger.info(PROCESS_START_LOG)
        model = YOLO(MRL_MODEL_PATH)
        input_image = preprocess_image(image_path)
        results = model(input_image)
        input_image = Image.open(image_path)

        output = []
        mrz_data = {"MRL_One": None, "MRL_Second": None}

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                label = result.names[cls_id]
                bbox = box.xyxy.tolist()[0]

                cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
                padded_image = add_fixed_padding(cropped_image)
                cropped_np = np.array(padded_image)
                cropped_cv2 = cv2.cvtColor(cropped_np, cv2.COLOR_RGB2BGR)

                if label in ["MRL_One", "MRL_Second"]:
                    text = extract_text_paddle(cropped_cv2)
                    mrz_data[label] = text
                else:
                    text = extract_text_doctr(cropped_cv2)
                    output.append({'Label': label, 'Extracted Text': text})

        if mrz_data["MRL_One"] and mrz_data["MRL_Second"]:
            mrz_df = parse_mrz(mrz_data["MRL_One"], mrz_data["MRL_Second"])
            output.extend(mrz_df.to_dict(orient="records"))

        df = pd.DataFrame(output)
        logger.info(PROCESS_COMPLETE_LOG)
        return df

    except Exception as e:
        logger.exception(PROCESS_EXCEPTION_LOG)
        return pd.DataFrame(columns=["Label", "Extracted Text"])
