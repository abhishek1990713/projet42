

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
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

app = FastAPI()


@app.post("/passport_details")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_ext = file.filename.split(".")[-1].lower()
        images = []

        if file_ext in ["jpg", "jpeg", "png"]:
            image_np = np.frombuffer(contents, np.uint8)
            image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            if image_cv2 is None:
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
                raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")

        elif file_ext in ["tiff", "tif"]:
            try:
                with BytesIO(contents) as tiff_io:
                    with Image.open(tiff_io) as img:
                        for frame in range(img.n_frames):
                            img.seek(frame)
                            image_cv2 = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
                            images.append(image_cv2)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to process TIFF: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")

        results = []

        for image in images:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                success, encoded_img = cv2.imencode(".jpg", image)
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to encode image.")
                temp_file.write(encoded_img.tobytes())
                temp_file_path = temp_file.name

            try:
                result_df = process_passport_information(temp_file_path)
                result_json = result_df.to_dict(orient='records')
                results.extend(result_json)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing passport: {str(e)}")
            finally:
                os.remove(temp_file_path)

        return JSONResponse(content={"status": "success", "data": results})

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unhandled server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)

