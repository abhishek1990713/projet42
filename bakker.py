

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
