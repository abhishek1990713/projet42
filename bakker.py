from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import shutil
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

# Setup logger
logger = setup_logger()

app = FastAPI()


@app.post("/passport_details")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")
        contents = await file.read()
        file_ext = file.filename.split(".")[-1].lower()
        images = []

        if file_ext in ["jpg", "jpeg", "png"]:
            logger.info("Processing image file")
            image_np = np.frombuffer(contents, np.uint8)
            image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            if image_cv2 is None:
                logger.error("Invalid image format")
                raise HTTPException(status_code=400, detail="Invalid image format.")
            images.append(image_cv2)

        elif file_ext == "pdf":
            logger.info("Processing PDF file")
            try:
                pdf_doc = fitz.open(stream=contents, filetype="pdf")
                for page_num, page in enumerate(pdf_doc):
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    images.append(image_cv2)
                    logger.info(f"Extracted page {page_num+1} from PDF")
            except Exception as e:
                logger.error(f"Failed to process PDF: {str(e)}", exc_info=True)
                raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")

        elif file_ext in ["tiff", "tif"]:
            logger.info("Processing TIFF file")
            try:
                with BytesIO(contents) as tiff_io:
                    with Image.open(tiff_io) as img:
                        for frame in range(img.n_frames):
                            img.seek(frame)
                            image_cv2 = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
                            images.append(image_cv2)
                            logger.info(f"Extracted frame {frame+1} from TIFF")
            except Exception as e:
                logger.error(f"Failed to process TIFF: {str(e)}", exc_info=True)
                raise HTTPException(status_code=400, detail=f"Failed to process TIFF: {str(e)}")

        else:
            logger.warning("Unsupported file format")
            raise HTTPException(status_code=400, detail="Unsupported file format.")

        results = []

        for idx, image in enumerate(images):
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                success, encoded_img = cv2.imencode(".jpg", image)
                if not success:
                    logger.error("Failed to encode image")
                    raise HTTPException(status_code=500, detail="Failed to encode image.")
                temp_file.write(encoded_img.tobytes())
                temp_file_path = temp_file.name
                logger.info(f"Temporary image file created: {temp_file_path}")

            try:
                logger.info(f"Processing image {idx+1}")
                result_df = process_passport_information(temp_file_path)
                result_json = result_df.to_dict(orient='records')
                results.extend(result_json)
                logger.info(f"Successfully extracted data from image {idx+1}")
            except Exception as e:
                logger.error(f"Error processing passport: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error processing passport: {str(e)}")
            finally:
                os.remove(temp_file_path)
                logger.info(f"Temporary file removed: {temp_file_path}")

        return JSONResponse(content={"status": "success", "data": results})

    except HTTPException as he:
        logger.warning(f"HTTPException raised: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unhandled server error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unhandled server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)

                
