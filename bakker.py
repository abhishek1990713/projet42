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
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from concurrent.futures import ThreadPoolExecutor
import shutil
from app import process_input
import os
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Directory for temporary file storage
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Thread pool for handling requests concurrently
executor = ThreadPoolExecutor(max_workers=4)

@app.post("/process-file/")
async def process_file(file: UploadFile = File(...)):
    """
    Endpoint to process an uploaded file (image or PDF) using multithreading.
    """
    try:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the file in a separate thread
        future = executor.submit(process_input, file_path)
        result = future.result()

        # Remove the file after processing
        os.remove(file_path)

        return JSONResponse(content={"status": "success", "result": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI OCR Processing Service!"}

@app.get("/health/")
async def health_check():
    return {"status": "ok", "message": "Service is running"}

@app.get("/config/")
async def get_config():
    return {"message": "This is the configuration route"}

if __name__ == "__main__":
    import argparse

    # Argument parser for dynamic port configuration
    parser = argparse.ArgumentParser(description="Run FastAPI server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the FastAPI server on")
    args = parser.parse_args()

    # Run FastAPI server with the specified port
    uvicorn.run(app, host="0.0.0.0", port=args.port)
