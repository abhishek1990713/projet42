

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
from arz.erl import parse_mrz_url
from many import extract_mrz_text  # Import the function from many.py

logging.getLogger('ppocr').setLevel(logging.WARNING)

os.environ["DOCTR_CACHE_DIR"] = r"/home/ko19678/all_passport_fast_api/DocTR_models"
os.environ['USE_TORCH'] = '1'

ocr_model = ocr_predictor(
    det_arch='db_resnet50',
    reco_arch='crnn_vgg16_bn',
    pretrained=True
)

det_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRV3_det_infer"
rec_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRV3_rec_infer"
cls_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"

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

passport_model_path = r"/home/ko19678/japan_pipeline/ALL_Passport/best.pt"

def preprocess_image(image_path):
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image

def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom

    if image.mode == 'RGB':
        color = (255, 255, 255)
    else:
        color = 0

    result = Image.new(image.mode, (new_width, new_height), color)
    result.paste(image, (left, top))
    return result

def extract_text_doctr(image_cv2):
    """Extract text using DocTR"""
    result_texts = ocr_model([image_cv2])
    extracted_text = ""
    if result_texts.pages:
        for page in result_texts.pages:
            for block in page.blocks:
                for line in block.lines:
                    extracted_text += "".join([word.value for word in line.words]) + " "
    return extracted_text.strip()

def extract_text_paddle(image_cv2):
    """Extract text using PaddleOCR"""
    result_texts = paddle_ocr.ocr(image_cv2, cls=False)
    extracted_text = ""
    if result_texts:
        for result in result_texts:
            for line in result:
                extracted_text += line[1][0] + " "
    return extracted_text.strip()

def process_passport_information(input_file_path):
    model = YOLO(passport_model_path)
    input_image = preprocess_image(input_file_path)
    results = model(input_image)

    input_image = Image.open(input_file_path)
    output = []
    mrz_data = {"MRL_One": None, "MRL_Second": None}
    nationality = "Unknown"

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            bbox = box.xyxy.tolist()[0]

            # Crop and pad image
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            padded_image = add_fixed_padding(cropped_image, right=100, left=100, top=100, bottom=100)
            cropped_image_np = np.array(padded_image)
            cropped_image_cv2 = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

            # If the label is "Nationality", check if it's "UNITED STATES OF AMERICA"
            if label == "Nationality":
                extracted_text = extract_text_paddle(cropped_image_cv2)
                print(f"Nationality: {extracted_text} ************")

                if extracted_text == "UNITED STATES OF AMERICA":
                    print("Extracting MRZ lines...")
                    mrz_data["MRL_One"], mrz_data["MRL_Second"] = extract_mrz_text(input_file_path)
                    print(f"MRL_One: {mrz_data['MRL_One']}, MRL_Second: {mrz_data['MRL_Second']}")
                else:
                    mrz_data[label] = extracted_text
            elif label in ["MRL_One", "MRL_Second"]:
                extracted_text = extract_text_paddle(cropped_image_cv2)
                print(f"{label}: {extracted_text} ************")
                mrz_data[label] = extracted_text
            else:
                extracted_text = extract_text_doctr(cropped_image_cv2)
                print(f"{label}: {extracted_text} @@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                output.append({'Label': label, 'Extracted Text': extracted_text})

    # If both MRZ lines were extracted, parse them
    if mrz_data["MRL_One"] and mrz_data["MRL_Second"]:
        mrz_df = parse_mrz(mrz_data["MRL_One"], mrz_data["MRL_Second"])
        output.extend(mrz_df.to_dict(orient="records"))

    data = pd.DataFrame(output)
    return data
