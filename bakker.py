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
    
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
from translator import translate_file
import uvicorn

app = FastAPI()

# Define paths for the models
PRETRAINED_LANG_MODEL = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
CHECKPOINT = r"C:\CitiDev\language_prediction\m2m"


@app.post("/translate/")
async def translate_file_endpoint(
    file: UploadFile = File(...), 
    target_language: str = Form(...)
):
    """
    Translate the uploaded file into the target language.

    Args:
        file (UploadFile): The file to be uploaded and translated.
        target_language (str): The target language for translation.

    Returns:
        dict: Translated content and metadata.
    """
    try:
        # Validate file extension
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ["txt", "pdf", "json"]:
            raise HTTPException(status_code=400, detail="Only TXT, PDF, and JSON files are supported.")

        # Save the uploaded file temporarily
        temp_file_path = f"temp.{file_extension}"
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        # Translate the file
        result = translate_file(
            file_path=temp_file_path,
            pretrained_lang_model=PRETRAINED_LANG_MODEL,
            checkpoint=CHECKPOINT,
            target_language=target_language
        )

        # Clean up the temporary file
        shutil.os.remove(temp_file_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
