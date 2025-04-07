

import os
import logging
import numpy as np
import cv2
import pandas as pd
import re
from PIL import Image
from ultralytics import YOLO
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from mrz_url import parse_wrz_url
from constant import (
    ENV_DOCTR_CACHE_DIR,
    ENV_USE_TORCH,
    LOG_PPOCR_LEVEL,
    PADDLE_MODEL_PATHS,
    YOLO_MODEL_PATH,
    ERROR_ENV_SETUP,
    ERROR_MODEL_INIT,
    ERROR_PREPROCESSING,
    ERROR_PADDING,
    ERROR_DOCTR_OCR,
    ERROR_PADDLE_OCR,
    ERROR_YOLO_LOAD,
    ERROR_YOLO_RUN,
    ERROR_BOX_PROCESS,
    ERROR_BBOX_PROCESS,
    ERROR_MRZ_PARSE,
    ERROR_DF_CREATE,
    LOG_EXTRACT_LABEL
)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger(LOG_PPOCR_LEVEL).setLevel(logging.WARNING)

# Environment setup
try:
    os.environ["DOCTR_CACHE_DIR"] = ENV_DOCTR_CACHE_DIR
    os.environ["USE_TORCH"] = ENV_USE_TORCH
except Exception as e:
    logger.error(f"{ERROR_ENV_SETUP}: {e}")

# Load models
try:
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

    det_model_dir = PADDLE_MODEL_PATHS['det']
    rec_model_dir = PADDLE_MODEL_PATHS['rec']
    cls_model_dir = PADDLE_MODEL_PATHS['cls']

    paddle_ocr = PaddleOCR(
        lang='en',
        use_angle_cls=False,
        use_gpu=False,
        det=True,
        rec=True,
        cls=False,
        det_model_dir=det_model_dir,
        rec_model_dir=rec_model_dir,
        cls_model_dir=cls_model_dir
    )
except Exception as e:
    logger.exception(f"{ERROR_MODEL_INIT}: {e}")
    raise

def preprocess_image(image_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.error(f"{ERROR_PREPROCESSING}: {e}")
        raise

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
        logger.error(f"{ERROR_PADDING}: {e}")
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
        logger.error(f"{ERROR_DOCTR_OCR}: {e}")
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
        logger.error(f"{ERROR_PADDLE_OCR}: {e}")
        return ""

def process_passport_information(input_file_path):
    try:
        model = YOLO(YOLO_MODEL_PATH)
    except Exception as e:
        logger.error(f"{ERROR_YOLO_LOAD}: {e}")
        raise

    try:
        input_image = preprocess_image(input_file_path)
        results = model(input_image)
        input_image = Image.open(input_file_path)
    except Exception as e:
        logger.error(f"{ERROR_YOLO_RUN}: {e}")
        raise

    output = []
    mrz_data = {"MRL_One": None, "MRL_Second": None}

    try:
        for result in results:
            boxes = result.boxes
            for box in boxes:
                try:
                    cls_id = int(box.cls[0])
                    label = result.names[cls_id]
                    bbox = box.xyxy.tolist()[0]

                    cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
                    padded_image = add_fixed_padding(cropped_image)
                    cropped_image_np = np.array(padded_image)
                    cropped_image_cv2 = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

                    if label in ["MRL_One", "MRL_Second"]:
                        extracted_text = extract_text_paddle(cropped_image_cv2)
                        logger.info(LOG_EXTRACT_LABEL.format(label, extracted_text))
                        mrz_data[label] = extracted_text
                    else:
                        extracted_text = extract_text_doctr(cropped_image_cv2)
                        logger.info(LOG_EXTRACT_LABEL.format(label, extracted_text))
                        output.append({'Label': label, 'Extracted Text': extracted_text})
                except Exception as e:
                    logger.warning(f"{ERROR_BOX_PROCESS}: {e}")
                    continue
    except Exception as e:
        logger.error(f"{ERROR_BBOX_PROCESS}: {e}")
        raise

    try:
        if mrz_data["MRL_One"] and mrz_data["MRL_Second"]:
            mrz_df = parse_wrz_url(mrz_data["MRL_One"], mrz_data["MRL_Second"])
            output.extend(mrz_df.to_dict(orient="records"))
    except Exception as e:
        logger.error(f"{ERROR_MRZ_PARSE}: {e}")

    try:
        data = pd.DataFrame(output)
        return data
    except Exception as e:
        logger.error(f"{ERROR_DF_CREATE}: {e}")
        raise
