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

import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from concurrent.futures import ThreadPoolExecutor
import uvicorn
import os

from main_app import process_input_file

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(
    filename="api_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()

# ThreadPoolExecutor for multithreading
executor = ThreadPoolExecutor(max_workers=5)


@app.post("/process-file/")
async def process_file(file: UploadFile = File(...)):
    """
    API endpoint to process an uploaded file (image or PDF).
    """
    try:
        # Save uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        logger.info(f"Received file: {file.filename}")
        result = await process_file_async(file_path)

        # Clean up temporary file
        os.remove(file_path)

        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during processing.")


async def process_file_async(file_path):
    """
    Asynchronous wrapper for processing files using ThreadPoolExecutor.
    """
    loop = executor.submit(process_input_file, file_path)
    result = await loop.result()
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
