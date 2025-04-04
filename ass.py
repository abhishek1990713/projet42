import logging
from constant import LOGGER_NAME, LOG_FILE_NAME, LOG_FORMAT

def setup_logger():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(LOG_FILE_NAME)
    formatter = logging.Formatter(LOG_FORMAT)
    fh.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(fh)

    return logger

logger = setup_logger()



# Logging Messages
LOG_PPOCR_LEVEL = 'ppocr'
LOGGING_LEVEL = 'WARNING'
LOGGER_NAME = 'passport_logger'
LOG_FILE_NAME = 'passport_app.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Paths
DOCTR_CACHE_DIR = '/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models/models/models'
PASSPORT_MODEL_PATH = '/home/ko19678/japan_pipeline/ALL_Passport/best.pt'
DET_MODEL_DIR = '/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer'
REC_MODEL_DIR = '/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer'
CLS_MODEL_DIR = '/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer'

# Labels
MRL_ONE = 'MRL_One'
MRL_SECOND = 'MRL_Second'

# Error Messages
ERR_IMAGE_DECODE = 'Unable to decode image'
ERR_IMAGE_PROCESS = 'Image processing error: '
ERR_PDF_PROCESS = 'PDF processing error: '
ERR_TIFF_PROCESS = 'TIFF processing error: '
ERR_UNSUPPORTED_FORMAT = 'Unsupported file format'
ERR_PROCESSING = 'Processing error: '

# Response
STATUS_SUCCESS = 'success'
STATUS_ERROR = 'error'

# Gender Mapping
GENDER_MAPPING = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}

# Date Validation
VALID_ISSUE_DATE = '22 AUG 2010'
VALID_EXPIRY_DATE = '22 AUG 2029'



from ultralytics import YOLO
from PIL import Image
import os
import numpy as np
import cv2
import pandas as pd
import re
from paddleocr import PaddleOCR
from doctr.models import ocr_predictor
from logger_config import logger
from constant import *

# Set PaddleOCR logging
logging.getLogger(LOG_PPOCR_LEVEL).setLevel(LOGGING_LEVEL)

# Set environment variables
os.environ["DOCTR_CACHE_DIR"] = DOCTR_CACHE_DIR
os.environ['USE_TORCH'] = '1'

ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)

paddle_ocr = PaddleOCR(
    lang='en',
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
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise

def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom
    color = (255, 255, 255)
    result = Image.new(image.mode, (new_width, new_height), color)
    result.paste(image, (left, top))
    return result

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
        logger.error(f"PaddleOCR extraction error: {e}")
        raise

def parse_mrz(mrz1, mrz2):
    try:
        mrz1 = mrz1.ljust(44, "<")[:44]
        mrz2 = mrz2.ljust(44, "<")[:44]

        document_type = mrz1[:2].strip("<")
        country_code = mrz1[2:5]
        names_part = mrz1[5:].split("<<", 1)
        surname = re.sub(r"<+", "", names_part[0]).strip()
        given_names = re.sub(r"<+", "", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

        passport_number = re.sub(r"<+$", "", mrz2[:9])
        nationality = mrz2[10:13].strip("<")

        def format_date(yyMMdd):
            if len(yyMMdd) != 6 or not yyMMdd.isdigit():
                return "Invalid Date"
            yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
            year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
            return f"{dd}/{mm}/{year}"

        dob = format_date(mrz2[13:19])
        expiry_date = format_date(mrz2[21:27])
        gender_code = mrz2[20]
        gender = GENDER_MAPPING.get(gender_code, "Unspecified")
        optional_data = re.sub(r"<+$", "", mrz2[28:]).strip()

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
        logger.error(f"Error parsing MRZ: {e}")
        raise

def process_passport_information(input_file_path):
    try:
        model = YOLO(PASSPORT_MODEL_PATH)
        input_image = preprocess_image(input_file_path)
        results = model(input_image)
        input_image = Image.open(input_file_path)

        output = []
        mrz_data = {MRL_ONE: None, MRL_SECOND: None}

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

                extracted_text = extract_text_paddle(cropped_image_cv2)

                if label in [MRL_ONE, MRL_SECOND]:
                    mrz_data[label] = extracted_text
                else:
                    output.append({'Label': label, 'Extracted Text': extracted_text})

        if mrz_data[MRL_ONE] and mrz_data[MRL_SECOND]:
            mrz_df = parse_mrz(mrz_data[MRL_ONE], mrz_data[MRL_SECOND])
            output.extend(mrz_df.to_dict(orient="records"))

        return pd.DataFrame(output)
    except Exception as e:
        logger.error(f"Error processing passport information: {e}")
        raise



from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import pandas as pd
from mrl_passport import process_passport_information
from constant import *
from logger_config import logger
import uvicorn
from io import BytesIO
import tempfile
import fitz
from PIL import Image
import traceback

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_ext = file.filename.split(".")[-1].lower()
        images = []

        if file_ext in ["jpg", "jpeg", "png"]:
            try:
                image_np = np.frombuffer(contents, np.uint8)
                image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
                if image_cv2 is None:
                    raise ValueError(ERR_IMAGE_DECODE)
                images.append(image_cv2)
            except Exception as e:
                logger.error(f"{ERR_IMAGE_PROCESS}{e}")
                raise HTTPException(status_code=400, detail=f"{ERR_IMAGE_PROCESS}{str(e)}")

        elif file_ext == "pdf":
            try:
                pdf_doc = fitz.open(stream=contents, filetype="pdf")
                for page in pdf_doc:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    images.append(image_cv2)
            except Exception as e:
                logger.error(f"{ERR_PDF_PROCESS}{e}")
                raise HTTPException(status_code=400, detail=f"{ERR_PDF_PROCESS}{str(e)}")

        elif file_ext in ["tiff", "tif"]:
            try:
                with BytesIO(contents) as tiff_io:
                    with Image.open(tiff_io) as img:
                        for frame in range(img.n_frames):
                            img.seek(frame)
                            image_cv2 = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
                            images.append(image_cv2)
            except Exception as e:
                logger.error(f"{ERR_TIFF_PROCESS}{e}")
                raise HTTPException(status_code=400, detail=f"{ERR_TIFF_PROCESS}{str(e)}")

        else:
            logger.error(ERR_UNSUPPORTED_FORMAT)
            raise HTTPException(status_code=400, detail=ERR_UNSUPPORTED_FORMAT)

        results = []
        for image in images:
            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    _, encoded_img = cv2.imencode(".jpg", image)
                    temp_file.write(encoded_img.tobytes())
                    temp_file_path = temp_file.name

                result_df = process_passport_information(temp_file_path)
                results.extend(result_df.to_dict(orient="records"))
            except Exception as e:
                logger.error(f"{ERR_PROCESSING}{e}")
                raise HTTPException(status_code=500, detail=f"{ERR_PROCESSING}{str(e)}")

        return JSONResponse(content={"status": STATUS_SUCCESS, "data": results})

    except Exception as e:
        error_message = traceback.format_exc()
        logger.error(f"{STATUS_ERROR}: {str(e)}\n{error_message}")
        return JSONResponse(status_code=500, content={"status": STATUS_ERROR, "message": str(e), "trace": error_message})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)

