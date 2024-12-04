from flask import Flask, jsonify, request
import ssl

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello, client! Connection is secure."})

if __name__ == '__main__':
    # SSL context configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.verify_mode = ssl.CERT_REQUIRED  # Require client certificate verification
    context.load_cert_chain(certfile='certificate.cer', keyfile='private.key')
    context.load_verify_locations(cafile='CA.pem')  # Load the CA certificate for client verification
    
    # Run the Flask app with SSL enabled
    app.run(host='127.0.0.1', port=8013, ssl_context=context)

# Define constants for the model path and other parameters
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import os
import logging
from main import process_image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("fastapi.log"), logging.StreamHandler()],
)

app = FastAPI()

# Temporary folders
UPLOAD_FOLDER = Path("uploads")
PROCESSED_FOLDER = Path("processed")

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

# Thread pool executor for multithreading
executor = ThreadPoolExecutor(max_workers=5)


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        input_image_path = UPLOAD_FOLDER / file.filename
        with open(input_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Define output path for the processed image
        output_image_path = PROCESSED_FOLDER / f"processed_{file.filename}"

        # Process the image in a separate thread
        future = executor.submit(process_image, str(input_image_path), str(output_image_path))
        result = future.result()

        if result["status"] == "success":
            return FileResponse(result["output"], media_type="image/png", filename=f"processed_{file.filename}")
        else:
            return {"status": "error", "message": result["message"]}
    except Exception as e:
        logging.error(f"Error in /upload/: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Image Processing API"}
