from flask import Flask, jsonify, request
import ssl

app = Flask(__name__)

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from application import initialize_models, translate_file
import shutil
import os

# Initialize FastAPI app
app = FastAPI()

# Port configuration
PORT = 8888

# Paths for the models
LANG_MODEL_PATH = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
TRANSLATION_MODEL_PATH = r"C:\CitiDev\language_prediction\m2m"

# Initialize models at startup
lang_model, translation_pipeline = initialize_models(LANG_MODEL_PATH, TRANSLATION_MODEL_PATH)


@app.post("/translate/")
async def translate_file_api(
    file: UploadFile = File(...), 
    target_language: str = Form(...)
):
    """
    API Endpoint to translate a file (PDF, TXT, JSON).
    
    Args:
        file (UploadFile): Uploaded file to be translated.
        target_language (str): Target language for translation.

    Returns:
        JSON response with translation details.
    """
    try:
        # Save the uploaded file temporarily
        temp_file_path = os.path.join("temp", file.filename)
        os.makedirs("temp", exist_ok=True)

        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        # Call the translate_file function from application.py
        result = translate_file(temp_file_path, lang_model, translation_pipeline, target_language)

        # Clean up the temporary file
        os.remove(temp_file_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def read_root():
    """
    Root endpoint to test if the API is running.
    """
    return {"message": "Translation API is running on port 8888."}


# Run the FastAPI app on port 8888
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fast:app", host="0.0.0.0", port=PORT, reload=True)
