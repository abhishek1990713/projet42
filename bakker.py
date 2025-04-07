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
logger.info("mrl_passport.py loaded")

os.environ["DOCTR_CACHE_DIR"] = r"/home/ko19678/japan_pipeline/ALL_Passport/DocTR_Models/models/models"
os.environ['USE_TORCH'] = '1'

try:
    logger.info("Loading DocTR model")
    ocr_model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    logger.info("DocTR model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load doctr model: {e}")
    raise

logger.info("Loading PaddleOCR model")
det_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_det_infer"
rec_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/en_PP-OCRv3_rec_infer"
cls_model_dir = r"/home/ko19678/japan_pipeline/japan_pipeline/paddle_model/ch_ppocr_mobile_v2.0_cls_infer"

try:
    paddle_ocr = PaddleOCR(lang='en', use_angle_cls=False, use_gpu=False, det=True, rec=True,
                           cls=False, det_model_dir=det_model_dir, rec_model_dir=rec_model_dir,
                           cls_model_dir=cls_model_dir)
    logger.info("PaddleOCR model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load paddleocr model: {e}")
    raise

passport_model_path = r"/home/ko19678/japan_pipeline/ALL_Passport/best.pt"

def preprocess_image(image_path):
    logger.info(f"Preprocessing image: {image_path}")
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        logger.info("Image preprocessed successfully")
        return image
    except Exception as e:
        logger.exception("Error in preprocess_image")
        raise

def add_fixed_padding(image, right=100, left=100, top=100, bottom=100):
    logger.info("Adding fixed padding to image")
    try:
        width, height = image.size
        new_width = width + right + left
        new_height = height + top + bottom
        color = (255, 255, 255) if image.mode == 'RGB' else 255
        result = Image.new(image.mode, (new_width, new_height), color)
        result.paste(image, (left, top))
        logger.info("Fixed padding added successfully")
        return result
    except Exception as e:
        logger.exception("Error in add_fixed_padding")
        raise

def extract_text_doctr(image_cv2):
    logger.info("Extracting text using DocTR")
    try:
        result_texts = ocr_model([image_cv2])
        extracted_text = ""
        if result_texts.pages:
            for page in result_texts.pages:
                for block in page.blocks:
                    for line in block.lines:
                        extracted_text += " ".join([word.value for word in line.words]) + " "
        logger.info("DocTR text extraction completed")
        return extracted_text.strip()
    except Exception as e:
        logger.exception("Error in extract_text_doctr")
        raise

def extract_text_paddle(image_cv2):
    logger.info("Extracting text using PaddleOCR")
    try:
        result_texts = paddle_ocr.ocr(image_cv2, cls=False)
        extracted_text = ""
        if result_texts:
            for result in result_texts:
                for line in result:
                    extracted_text += line[1][0] + " "
        logger.info("PaddleOCR text extraction completed")
        return extracted_text.strip()
    except Exception as e:
        logger.exception("PaddleOCR extraction failed")
        raise

def parse_mrz(mrl1, mrl2):
    logger.info("Parsing MRZ lines")
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
        logger.info("MRZ parsing completed")
        return df
    except Exception as e:
        logger.exception("Error in parse_mrz")
        raise


from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import fitz  # PyMuPDF
import tempfile
import uvicorn
import os

from mrl_passport import process_passport_information
from logger_config import setup_logger

logger = setup_logger("app_logger", "passport.log")

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    logger.info("Received file upload request")
    try:
        contents = await file.read()
        logger.info(f"Successfully read file: {file.filename}")
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    file_ext = file.filename.split(".")[-1].lower()
    images = []

    try:
        if file_ext in ["jpg", "jpeg", "png"]:
            logger.info("Processing as image file")
            image_np = np.frombuffer(contents, np.uint8)
            image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            if image_cv2 is None:
                logger.error("Invalid image format")
                raise HTTPException(status_code=400, detail="Invalid image format.")
            images.append(image_cv2)

        elif file_ext == "pdf":
            logger.info("Processing as PDF file")
            try:
                pdf_doc = fitz.open(stream=contents, filetype="pdf")
                for page in pdf_doc:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    images.append(image_cv2)
            except Exception as e:
                logger.error(f"Failed to process PDF: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")

        elif file_ext in ["tiff", "tif"]:
            logger.info("Processing as TIFF file")
            try:
                with BytesIO(contents) as tiff_io:
                    with Image.open(tiff_io) as img:
                        for frame in range(img.n_frames):
                            img.seek(frame)
                            image_cv2 = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
                            images.append(image_cv2)
            except UnidentifiedImageError:
                logger.error("Cannot identify TIFF image")
                raise HTTPException(status_code=400, detail="Cannot identify TIFF image.")
            except Exception as e:
                logger.error(f"Failed to process TIFF: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to process TIFF: {str(e)}")

        else:
            logger.error("Unsupported file format")
            raise HTTPException(status_code=400, detail="Unsupported file format.")

    except HTTPException as http_err:
        logger.warning(f"HTTP error during image extraction: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

    results = []

    for idx, image in enumerate(images):
        try:
            logger.info(f"Processing image {idx + 1}/{len(images)}")
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                success, encoded_img = cv2.imencode(".jpg", image)
                if not success:
                    logger.error("Failed to encode image")
                    raise ValueError("Failed to encode image.")
                temp_file.write(encoded_img.tobytes())
                temp_file_path = temp_file.name

            logger.info(f"Temporary file created: {temp_file_path}")
            result_df = process_passport_information(temp_file_path)

            if result_df is None:
                logger.warning(f"No data extracted from image {idx + 1}")
                raise ValueError("No data extracted from passport.")

            result_json = result_df.to_dict(orient='records')
            results.extend(result_json)
            logger.info(f"Extraction complete for image {idx + 1}")

            os.remove(temp_file_path)
            logger.info(f"Temporary file deleted: {temp_file_path}")

        except Exception as e:
            logger.error(f"Error during passport processing for image {idx+1}: {e}")
            raise HTTPException(status_code=500, detail=f"Error during passport processing for image {idx+1}: {str(e)}")

    logger.info("All image processing complete, returning results")
    return JSONResponse(content={"status": "success", "data": results})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
