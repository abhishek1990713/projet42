from flask import Flask, jsonify, request
import ssl

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from application import initialize_models, translate_file
import shutil
import os
import threading
import logging

# Setup logging
LOG_FILE = "api_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Initialize FastAPI app
app = FastAPI()

# Port configuration
PORT = 8888

# Paths for the models
LANG_MODEL_PATH = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
TRANSLATION_MODEL_PATH = r"C:\CitiDev\language_prediction\m2m"

# Initialize models at startup
try:
    lang_model, translation_pipeline = initialize_models(LANG_MODEL_PATH, TRANSLATION_MODEL_PATH)
except RuntimeError as e:
    logging.error(f"Model initialization failed: {e}")
    raise RuntimeError(f"Model initialization failed: {e}")


@app.post("/translate/")
async def translate_file_api(
    file: UploadFile = File(...),
    target_language: str = Form(...)
):
    """
    API Endpoint to translate a file (PDF, TXT, JSON).
    """
    try:
        temp_file_path = os.path.join("temp", file.filename)
        os.makedirs("temp", exist_ok=True)

        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        def process_translation():
            try:
                result = translate_file(temp_file_path, lang_model, translation_pipeline, target_language)
                os.remove(temp_file_path)
                return result
            except Exception as e:
                os.remove(temp_file_path)
                raise e

        thread = threading.Thread(target=process_translation)
        thread.start()
        thread.join()

        return {"status": "success", "message": "Translation completed. Check logs for details."}

    except Exception as e:
        logging.error(f"Error in translate_file_api: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    logging.info("Root endpoint accessed.")
    return {"message": "Translation API is running on port 8888."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fast:app", host="0.0.0.0", port=PORT, reload=True)
