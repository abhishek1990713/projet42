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
import uvicorn
from main import process_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("fastapi.log"), logging.StreamHandler()],
)

app = FastAPI()

UPLOAD_FOLDER = Path("uploads")
PROCESSED_FOLDER = Path("processed")

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

executor = ThreadPoolExecutor(max_workers=5)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    logging.info(f"Received file: {file.filename}")
    try:
        input_image_path = UPLOAD_FOLDER / file.filename
        with open(input_image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_image_path = PROCESSED_FOLDER / f"processed_{file.filename}"
        logging.info(f"Processing image: {input_image_path} -> {output_image_path}")
        future = executor.submit(process_image, str(input_image_path), str(output_image_path))
        result = future.result()

        if result["status"] == "success":
            logging.info(f"Image processed successfully: {output_image_path}")
            return FileResponse(result["output"], media_type="image/png", filename=f"processed_{file.filename}")
        else:
            logging.error(f"Error processing image: {result['message']}")
            return {"status": "error", "message": result["message"]}
    except Exception as e:
        logging.error(f"Exception in upload_image: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Image Processing API"}

# Run the app on port 8888
if __name__ == "__main__":
    uvicorn.run("fast:app", host="0.0.0.0", port=8888, reload=True)
