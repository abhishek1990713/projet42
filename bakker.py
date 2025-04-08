# constant.py

# API Paths
API_ROUTE_PASSPORT_DETAILS = "/passport_details"

# File Extensions
FILE_EXT_IMAGE = ["jpg", "jpeg", "png"]
FILE_EXT_PDF = "pdf"
FILE_EXT_TIFF = ["tiff", "tif"]

# Status
RESPONSE_STATUS_SUCCESS = "success"

# Logging Messages
LOG_RECEIVED_FILE = "Received file: {}"
LOG_PROCESSING_IMAGE = "Processing image file"
LOG_INVALID_IMAGE = "Invalid image format"
LOG_PROCESSING_PDF = "Processing PDF file"
LOG_PDF_PAGE_EXTRACTED = "Extracted page {} from PDF"
LOG_FAILED_PDF = "Failed to process PDF: {}"
LOG_PROCESSING_TIFF = "Processing TIFF file"
LOG_TIFF_FRAME_EXTRACTED = "Extracted frame {} from TIFF"
LOG_FAILED_TIFF = "Failed to process TIFF: {}"
LOG_UNSUPPORTED_FILE = "Unsupported file format"
LOG_TEMP_FILE_CREATED = "Temporary image file created: {}"
LOG_PROCESSING_IMAGE_NUM = "Processing image {}"
LOG_PROCESS_SUCCESS = "Successfully extracted data from image {}"
LOG_PROCESS_ERROR = "Error processing passport: {}"
LOG_TEMP_FILE_REMOVED = "Temporary file removed: {}"
LOG_HTTP_EXCEPTION = "HTTPException raised: {}"
LOG_UNHANDLED_ERROR = "Unhandled server error: {}"

# Error Details
ERROR_INVALID_IMAGE = "Invalid image format."
ERROR_UNSUPPORTED_FORMAT = "Unsupported file format."
ERROR_FAILED_TO_ENCODE = "Failed to encode image."
ERROR_PROCESSING_PDF = "Failed to process PDF: {}"
ERROR_PROCESSING_TIFF = "Failed to process TIFF: {}"
ERROR_PROCESSING_PASSPORT = "Error processing passport: {}"
ERROR_UNHANDLED = "Unhandled server error: {}"
 




from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import List
from mrl_passport import process_passport_information
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import pandas as pd
import tempfile
import fitz  # PyMuPDF
from setup import setup_logger
import constant

# Setup logger
logger = setup_logger()

app = FastAPI()


@app.post(constant.API_ROUTE_PASSPORT_DETAILS)
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(constant.LOG_RECEIVED_FILE.format(file.filename))
        contents = await file.read()
        file_ext = file.filename.split(".")[-1].lower()
        images = []

        if file_ext in constant.FILE_EXT_IMAGE:
            logger.info(constant.LOG_PROCESSING_IMAGE)
            image_np = np.frombuffer(contents, np.uint8)
            image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            if image_cv2 is None:
                logger.error(constant.LOG_INVALID_IMAGE)
                raise HTTPException(status_code=400, detail=constant.ERROR_INVALID_IMAGE)
            images.append(image_cv2)

        elif file_ext == constant.FILE_EXT_PDF:
            logger.info(constant.LOG_PROCESSING_PDF)
            try:
                pdf_doc = fitz.open(stream=contents, filetype="pdf")
                for page_num, page in enumerate(pdf_doc):
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    images.append(image_cv2)
                    logger.info(constant.LOG_PDF_PAGE_EXTRACTED.format(page_num + 1))
            except Exception as e:
                logger.error(constant.LOG_FAILED_PDF.format(str(e)), exc_info=True)
                raise HTTPException(status_code=400, detail=constant.ERROR_PROCESSING_PDF.format(str(e)))

        elif file_ext in constant.FILE_EXT_TIFF:
            logger.info(constant.LOG_PROCESSING_TIFF)
            try:
                with BytesIO(contents) as tiff_io:
                    with Image.open(tiff_io) as img:
                        for frame in range(img.n_frames):
                            img.seek(frame)
                            image_cv2 = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
                            images.append(image_cv2)
                            logger.info(constant.LOG_TIFF_FRAME_EXTRACTED.format(frame + 1))
            except Exception as e:
                logger.error(constant.LOG_FAILED_TIFF.format(str(e)), exc_info=True)
                raise HTTPException(status_code=400, detail=constant.ERROR_PROCESSING_TIFF.format(str(e)))

        else:
            logger.warning(constant.LOG_UNSUPPORTED_FILE)
            raise HTTPException(status_code=400, detail=constant.ERROR_UNSUPPORTED_FORMAT)

        results = []

        for idx, image in enumerate(images):
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                success, encoded_img = cv2.imencode(".jpg", image)
                if not success:
                    logger.error(constant.ERROR_FAILED_TO_ENCODE)
                    raise HTTPException(status_code=500, detail=constant.ERROR_FAILED_TO_ENCODE)
                temp_file.write(encoded_img.tobytes())
                temp_file_path = temp_file.name
                logger.info(constant.LOG_TEMP_FILE_CREATED.format(temp_file_path))

            try:
                logger.info(constant.LOG_PROCESSING_IMAGE_NUM.format(idx + 1))
                result_df = process_passport_information(temp_file_path)
                result_json = result_df.to_dict(orient='records')
                results.extend(result_json)
                logger.info(constant.LOG_PROCESS_SUCCESS.format(idx + 1))
            except Exception as e:
                logger.error(constant.LOG_PROCESS_ERROR.format(str(e)), exc_info=True)
                raise HTTPException(status_code=500, detail=constant.ERROR_PROCESSING_PASSPORT.format(str(e)))
            finally:
                os.remove(temp_file_path)
                logger.info(constant.LOG_TEMP_FILE_REMOVED.format(temp_file_path))

        return JSONResponse(content={"status": constant.RESPONSE_STATUS_SUCCESS, "data": results})

    except HTTPException as he:
        logger.warning(constant.LOG_HTTP_EXCEPTION.format(he.detail))
        raise he
    except Exception as e:
        logger.error(constant.LOG_UNHANDLED_ERROR.format(str(e)), exc_info=True)
        raise HTTPException(status_code=500, detail=constant.ERROR_UNHANDLED.format(str(e)))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
