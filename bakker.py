

from ultralytics import YOLO
from PIL import Image
import logging
import re
from paddleocr import PaddleOCR
import contants_info

# Configure logging
logging.getLogger('ppocr').setLevel(logging.WARNING)

# Initialize OCR model
ocr = PaddleOCR(
    lang='japan',
    use_angle_cls=False,
    use_gpu=False,
    det=True,
    rec=True,
    cls=False,
    det_model_dir=contants_info.DET_MODEL_DIR,
    rec_model_dir=contants_info.REC_MODEL_DIR,
    cls_model_dir=contants_info.CLS_MODEL_DIR
)

driving_license_model_path = r"C:\AS34751\Downloads\dl_information.pt"
min_expire_year = contants_info.Rin_expire_year
max_expire_year = contants_info.Max_expire_year

# Function to convert era to Gregorian year
def era_to_gregorian(era_year, era_name):
    """Convert Japanese era year to Gregorian year"""
    era_map = {
        "令和": 2019,  # Reiwa starts in 2019
        "昭和": 1926,  # Showa starts in 1926
        "平成": 1989,  # Heisei starts in 1989
    }
    if era_name in era_map:
        return era_map[era_name] + era_year - 1
    return None  # For unknown eras

# Function to process driving license information
def process_dl_information(input_file_path):
    model = YOLO(driving_license_model_path)
    results = model(input_file_path)

    input_image = Image.open(input_file_path)
    output = []

    for result in results:
        boxes = result.boxes

        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            bbox = box.xyxy[0].tolist()

            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            cropped_image_np = np.array(cropped_image)

            result_texts = ocr.ocr(cropped_image_np, cls=False)

            if result_texts and result_texts[0]:
                extracted_text = ' '.join([text[1][0] for text in result_texts[0]])
            else:
                extracted_text = ""

            print(f"Detected {label}: {extracted_text}")
            output.append(f"Detected Label: {label}: {extracted_text}")

            if label == "Expiration date":
                # Extract year using regex and handle era
                year_match = re.search(r"(\d{4})年|(\w+)(\d+)年", extracted_text)
                if year_match:
                    if year_match.group(1):  # If it's a direct year
                        year = int(year_match.group(1))
                    else:  # Handle era-based year
                        era_name = year_match.group(2)
                        era_year = int(year_match.group(3))
                        year = era_to_gregorian(era_year, era_name)
                    
                    if min_expire_year <= year <= max_expire_year:
                        output.append(f"Year {year} is within the valid range ({min_expire_year}-{max_expire_year}).")
                    else:
                        output.append(f"Year {year} is outside the valid range ({min_expire_year}-{max_expire_year}).")
                else:
                    output.append("Year not found in 'Expiration date' text.")

            if label == "DOB":
                # Extract year using regex and handle era for DOB
                dob_match = re.search(r"(\w+)(\d+)年(\d+)月(\d+)日生", extracted_text)
                if dob_match:
                    era_name = dob_match.group(1)
                    era_year = int(dob_match.group(2))
                    dob_year = era_to_gregorian(era_year, era_name)
                    output.append(f"Extracted DOB Year: {dob_year}")
                else:
                    output.append("Year not found in 'DOB' text.")

    return output

input_file_path = r"C:\CitiDev\Japan_pipeline\data_set\japan_test_image\6f7rch30 4.png"
result = process_dl_information(input_file_path)
print(result)
