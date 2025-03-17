


import os
import cv2
import re
import pandas as pd
import numpy as np
from PIL import Image
import logging
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from ultralytics import YOLO

# Suppress PaddleOCR warnings
logging.getLogger("ppocr").setLevel(logging.WARNING)

# DocTR Configuration
os.environ["DOCTR_CACHE_DIR"] = r"/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models"
os.environ["USE_TORCH"] = "1"

# Initialize DocTR OCR model
ocr_model = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True)

# PaddleOCR Configuration (For MRZ Fields Only)
det_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
rec_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
cls_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"

paddle_ocr = PaddleOCR(
    lang="en",
    use_angle_cls=False,
    use_gpu=False,
    det=True,
    rec=True,
    cls=False,
    det_model_dir=det_model_dir,
    rec_model_dir=rec_model_dir,
    cls_model_dir=cls_model_dir,
)

# Passport YOLO Model Path
passport_model_path = r"/home/ko19678/japan_pipeline/ALL_Passport/best.pt"

# Function to preprocess images
def preprocess_image(image_path):
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image

# Function to add padding
def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom
    color = 255 if image.mode == "RGB" else 0
    result = Image.new(image.mode, (new_width, new_height), color)
    result.paste(image, (left, top))
    return result

# Function to process MRZ fields using PaddleOCR
def extract_mrz_with_paddle(cropped_image):
    cropped_image_np = np.array(cropped_image)
    cropped_image_cv2 = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)
    result = paddle_ocr.ocr(cropped_image_cv2, cls=False)
    extracted_text = ""
    if result and result[0]:
        extracted_text = " ".join([res[1][0] for res in result[0]])
    return extracted_text.strip()

# Function to process passport information
def process_passport_information(input_file_path):
    model = YOLO(passport_model_path)
    input_image = preprocess_image(input_file_path)
    results = model(input_image)
    
    output = []
    mrz_one = None
    mrz_second = None

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            bbox = box.xyxy.tolist()[0]

            # Crop and pad the detected region
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            padded_image = add_fixed_padding(cropped_image, right=100, left=100, top=100, bottom=100)

            # Process MRL_One and MRL_Second with PaddleOCR
            if label in ["MRL_One", "MRL_Second"]:
                extracted_text = extract_mrz_with_paddle(padded_image)
                if label == "MRL_One":
                    mrz_one = extracted_text
                elif label == "MRL_Second":
                    mrz_second = extracted_text
            else:
                # Process all other labels with DocTR
                cropped_image_np = np.array(padded_image)
                cropped_image_cv2 = cv2.cvtColor(cropped_image_np, cv2.COLOR_RGB2BGR)
                result_texts = ocr_model([cropped_image_cv2])

                extracted_text = ""
                if result_texts.pages:
                    for page in result_texts.pages:
                        for block in page.blocks:
                            for line in block.lines:
                                extracted_text += " ".join([word.value for word in line.words]) + " "
                
                extracted_text = extracted_text.strip()
                output.append({"Label": label, "Extracted_text": extracted_text})

    # If MRZ fields are detected, parse them
    if mrz_one and mrz_second:
        mrz_data = parse_mrz(mrz_one, mrz_second)
        output.extend(mrz_data.to_dict(orient="records"))

    return pd.DataFrame(output)

# Function to parse MRZ data
def parse_mrz(mrl1, mrl2):
    """Extracts passport details from MRZ lines and returns a DataFrame."""
    
    # Ensure MRZ lines are padded to 44 characters
    mrl1 = mrl1.ljust(44, "<")[:44]
    mrl2 = mrl2.ljust(44, "<")[:44]

    # Extract document type
    document_type = mrl1[:2].strip("<")

    # Extract issuing country code
    country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"

    # Extract surname and given names
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if names_part else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

    # Extract passport number
    passport_number = mrl2[:9].replace("<", "") if len(mrl2) >= 9 else "Unknown"

    # Extract nationality
    nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else "Unknown"

    # Function to format date from YYMMDD to DD/MM/YYYY
    def format_date(yyMMdd):
        match = re.match(r"(\d{2})(\d{2})(\d{2})", yyMMdd)
        if not match:
            return "Invalid Date"
        yy, mm, dd = match.groups()
        year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
        return f"{dd}/{mm}/{year}"

    # Extract date of birth
    dob_raw = mrl2[13:19]
    dob = format_date(dob_raw) if len(dob_raw) == 6 else "Unknown"

    # Extract gender
    gender_code = mrl2[20] if len(mrl2) > 20 else "<"
    gender_mapping = {"M": "Male", "F": "Female", "<": "Unspecified"}
    gender = gender_mapping.get(gender_code, "Unspecified")

    # Extract expiry date
    expiry_raw = mrl2[21:27]
    expiry_date = format_date(expiry_raw) if len(expiry_raw) == 6 else "Unknown"

    # Extract personal number
    personal_number = mrl2[28:].replace("<", "").strip() if len(mrl2) > 28 else "N/A"

    # Create structured data for DataFrame
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
        ("Personal Number", personal_number if personal_number else "N/A"),
    ]

    return pd.DataFrame(data, columns=["Label", "Extracted_text"])
