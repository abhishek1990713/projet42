import re
import logging
import numpy as np
import pandas as pd
from PIL import Image
from datetime import datetime
from ultralytics import YOLO
import paddleocr

# Initialize OCR
ocr = paddleocr.PaddleOCR(lang='en')

# MRZ Parsing Function
def parse_mrz(mrl1, mrl2):
    mrl1 = mrl1.ljust(44, "<")[:44]  # Ensure 44 characters
    mrl2 = mrl2.ljust(44, "<")[:44]

    document_type = mrl1[:2].strip("<")
    country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"

    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if names_part else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

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

    return {
        "Document Type": document_type,
        "Issuing Country": country_code,
        "Surname": surname,
        "Given Names": given_names,
        "Passport Number": passport_number,
        "Nationality": nationality,
        "Date of Birth": dob,
        "Gender": gender,
        "Expiry Date": expiry_date,
        "Optional Data": optional_data if optional_data else "N/A",
    }

# Image Preprocessing
def preprocess_image(image_path):
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image

# Passport Processing Function
def process_passport_information(input_file_path):
    model_path = r"C:\Users\A534751\Downloads\best1.pt"
    model = YOLO(model_path)

    results = model(input_file_path)
    input_image = Image.open(input_file_path)

    output = []
    mrz_lines = []

    for result in results:
        boxes = result.boxes
        result.show()

        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]

            bbox = box.xyxy[0].tolist()
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

            cropped_image_np = np.array(cropped_image)
            result_texts = ocr.ocr(cropped_image_np, cls=False)

            extracted_text = "".join([text[1][0] for text in result_texts[0]]) if result_texts and result_texts[0] else ""

            output.append({'Label': label, 'Extracted_text': extracted_text})

            if label in ["MRL_One", "MRL_Second"]:
                mrz_lines.append(extracted_text)

    # Ensure we have two MRZ lines
    if len(mrz_lines) == 2:
        mrz_info = parse_mrz(mrz_lines[0], mrz_lines[1])
        for key, value in mrz_info.items():
            output.append({"Label": key, "Extracted_text": value})

    data = pd.DataFrame(output)
    return data

# Run the function
input_file_path = r"C:\CitiDev\japan_pipeline\data_set\passport\canada652.png"
print(process_passport_information(input_file_path()))

