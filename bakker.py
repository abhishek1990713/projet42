

# mrl_passport.py
from PIL import Image


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
import logging
from logger_config import setup_logger

from mrl_passport import process_passport_information  # Adjust the path as needed

logger = setup_logger("app", "app.log")

app = FastAPI()


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_ext = file.filename.split(".")[-1].lower()
        images = []

        if file_ext in ["jpg", "jpeg", "png"]:
            image_np = np.frombuffer(contents, np.uint8)
            image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            if image_cv2 is None:
                logger.error("Invalid image format.")
                raise HTTPException(status_code=400, detail="Invalid image format.")
            images.append(image_cv2)

        elif file_ext == "pdf":
            try:
                pdf_doc = fitz.open(stream=contents, filetype="pdf")
                for page in pdf_doc:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    images.append(image_cv2)
            except Exception as e:
                logger.exception("Failed to process PDF")
                raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")

        elif file_ext in ["tiff", "tif"]:
            try:
                with BytesIO(contents) as tiff_io:
                    with Image.open(tiff_io) as img:
                        for frame in range(img.n_frames):
                            img.seek(frame)
                            image_cv2 = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
                            images.append(image_cv2)
            except UnidentifiedImageError:
                logger.error("Cannot identify TIFF image.")
                raise HTTPException(status_code=400, detail="Cannot identify TIFF image.")
            except Exception as e:
                logger.exception("Failed to process TIFF")
                raise HTTPException(status_code=400, detail=f"Failed to process TIFF: {str(e)}")

        else:
            logger.error("Unsupported file format.")
            raise HTTPException(status_code=400, detail="Unsupported file format.")

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.exception("Image processing error")
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

    results = []

    for idx, image in enumerate(images):
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                success, encoded_img = cv2.imencode(".jpg", image)
                if not success:
                    logger.error("Failed to encode image.")
                    raise ValueError("Failed to encode image.")
                temp_file.write(encoded_img.tobytes())
                temp_file_path = temp_file.name

            result_df = process_passport_information(temp_file_path)

            if result_df is None:
                logger.warning(f"No data extracted from image {idx+1}.")
                raise ValueError("No data extracted from passport.")
            result_json = result_df.to_dict(orient='records')
            results.extend(result_json)

            os.remove(temp_file_path)

        except Exception as e:
            logger.exception(f"Error during passport processing for image {idx+1}")
            raise HTTPException(status_code=500, detail=f"Error during passport processing for image {idx+1}: {str(e)}")

    return JSONResponse(content={"status": "success", "data": results})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)


# logger_config.py
import logging
import os

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """Set up a logger with the given name and file."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate logs
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
