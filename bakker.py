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
    
import os
import json
import fasttext
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from datetime import datetime


# Load models
def initialize_models(lang_model_path, translation_model_path):
    lang_model = fasttext.load_model(lang_model_path)
    translation_model = AutoModelForSeq2SeqLM.from_pretrained(translation_model_path)
    tokenizer = AutoTokenizer.from_pretrained(translation_model_path)
    translation_pipeline = pipeline(
        'translation',
        model=translation_model,
        tokenizer=tokenizer,
        max_length=400
    )
    return lang_model, translation_pipeline


# Detect the language of text
def detect_language(text, lang_model):
    prediction = lang_model.predict(text.strip().replace("\n", ""))
    return prediction[0][0].replace("__label__", ""), prediction[1][0]


# Extract text based on file type
def extract_text(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == ".pdf":
        try:
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            return text
        except Exception as e:
            return {"status": "error", "message": f"Error reading PDF: {e}"}
    
    elif file_extension == ".txt":
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            return {"status": "error", "message": f"Error reading TXT file: {e}"}
    
    elif file_extension == ".json":
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, dict) and "text" in data:
                    return data["text"]
                else:
                    return {"status": "error", "message": "JSON file must contain a 'text' key."}
        except Exception as e:
            return {"status": "error", "message": f"Error reading JSON file: {e}"}
    
    else:
        return {"status": "error", "message": "Unsupported file format."}


# Translate file content
def translate_file(file_path, lang_model, translation_pipeline, target_language='en'):
    text = extract_text(file_path)
    if isinstance(text, dict) and text.get("status") == "error":
        return text  # Return error message if text extraction failed

    if not text:
        return {"status": "error", "message": "Input file is empty or has no readable text."}

    segments = text.split("\n")
    translated_segments = []
    log_entries = []

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        detected_language, confidence = detect_language(segment, lang_model)
        log_entries.append(
            {
                "segment": segment,
                "detected_language": detected_language,
                "confidence": confidence
            }
        )

        try:
            output = translation_pipeline(
                segment,
                src_lang=detected_language,
                tgt_lang=target_language
            )
            translated_text = output[0]['translation_text']
            translated_segments.append({"original": segment, "translated": translated_text})
        except Exception as e:
            translated_segments.append({"original": segment, "translated": None, "error": str(e)})

    return {
        "status": "success",
        "original_text": text,
        "translated_text": "\n".join([t["translated"] or "" for t in translated_segments]),
        "details": translated_segments,
        "log": log_entries
    }


# Example usage
if __name__ == "__main__":
    # Paths for the models
    lang_model_path = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
    translation_model_path = r"C:\CitiDev\language_prediction\m2m"

    # Initialize models
    lang_model, translation_pipeline = initialize_models(lang_model_path, translation_model_path)

    # Input file path
    input_file = r"C:\CitiDev\language_prediction\input_file.pdf"  # Change to your file path

    # Translate and get the output in JSON format
    output = translate_file(input_file, lang_model, translation_pipeline, target_language="en")

    # Print JSON output
    print(json.dumps(output, indent=4, ensure_ascii=False))
