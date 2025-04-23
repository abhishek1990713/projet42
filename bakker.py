
import os
import logging
import cv2
import re
import numpy as np
import pandas as pd
from PIL import Image
from ultralytics import YOLO
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from many import extract_mrz_text  # Import from many.py

# Setup environment
os.environ["DOCTR_CACHE_DIR"] = r"/home/ko19678/all_passport_fast_api/DocTR_models"
os.environ['USE_TORCH'] = '1'
logging.getLogger('ppocr').setLevel(logging.WARNING)

# Load OCR models
ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

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
    color = (255, 255, 255) if image.mode == 'RGB' else 0
    result = Image.new(image.mode, (new_width, new_height), color)
    result.paste(image, (left, top))
    return result

def extract_text_doctr(image_cv2):
    result_texts = ocr_model([image_cv2])
    extracted_text = ""
    if result_texts.pages:
        for page in result_texts.pages:
            for block in page.blocks:
                for line in block.lines:
                    extracted_text += "".join([word.value for word in line.words]) + " "
    return extracted_text.strip()

def extract_text_paddle(image_cv2):
    result_texts = paddle_ocr.ocr(image_cv2, cls=False)
    extracted_text = ""
    if result_texts:
        for result in result_texts:
            for line in result:
                extracted_text += line[1][0] + " "
    return extracted_text.strip()

def parse_mrz(mrl1, mrl2):
    mrl1 = mrl1.ljust(44, "<")[:44]
    mrl2 = mrl2.ljust(44, "<")[:44]
    document_type = mrl1[0:2].strip("<")
    country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", "", names_part[0]).strip() if names_part else "Unknown"
    given_names = re.sub(r"<+", "", names_part[1]).strip() if len(names_part) > 1 else "Unknown"
    passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) > 9 else "Unknown"
    nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else "Unknown"

    def format_date(yyMMdd):
        if len(yyMMdd) != 6 or not yyMMdd.isdigit():
            return "Invalid Date"
        yy, m, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
        year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
        return f"{dd}/{m}/{year}"

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
        ("Expiry Date", expiry_date)
    ]
    return pd.DataFrame(data, columns=["Label", "Extracted Text"])

def process_passport_information(image_path):
    model = YOLO(passport_model_path)
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
            cropped_image_np = np.array(padded_image)
            cropped_image_cv2 = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)

            if label in ["MRL_One", "MRL_Second"]:
                extracted_text = extract_text_paddle(cropped_image_cv2)
                mrz_data[label] = extracted_text
            else:
                extracted_text = extract_text_doctr(cropped_image_cv2)

            print(f"{label}: {extracted_text}")
            output.append({'Label': label, 'Extracted Text': extracted_text})

            # Check nationality condition
            if label.lower() == "nationality" and extracted_text.strip().lower() in [
                "unitedstateof america, usa", "usa", "united states", "united states of america"
            ]:
                print("Nationality matched condition — extracting MRZ from many.py...")
                mrl_one, mrl_second = extract_mrz_text(image_path)
                print("MRL Line 1:", mrl_one)
                print("MRL Line 2:", mrl_second)
                parsed_df = parse_mrz(mrl_one, mrl_second)
                output.extend(parsed_df.to_dict(orient="records"))

    # Parse MRZ from YOLO if not done above
    if mrz_data["MRL_One"] and mrz_data["MRL_Second"]:
        mrz_df = parse_mrz(mrz_data["MRL_One"], mrz_data["MRL_Second"])
        output.extend(mrz_df.to_dict(orient="records"))

    return pd.DataFrame(output)
