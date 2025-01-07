from flask import Flask, jsonify, request
import ssl

import os
import json
import fasttext
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from datetime import datetime
import logging

# Configure logging with UTF-8 support
LOG_FILE = "translation_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(file_handler)


def log_message(message):
    logging.info(message)
    print(message)


# Load models
def initialize_models(lang_model_path, translation_model_path):
    log_message("Initializing models...")
    try:
        lang_model = fasttext.load_model(lang_model_path)
        log_message("Language model loaded successfully.")
    except Exception as e:
        log_message(f"Error loading FastText model: {e}")
        raise RuntimeError(f"Error loading FastText model: {e}")

    try:
        translation_model = AutoModelForSeq2SeqLM.from_pretrained(translation_model_path)
        tokenizer = AutoTokenizer.from_pretrained(translation_model_path)
        translation_pipeline = pipeline(
            'translation',
            model=translation_model,
            tokenizer=tokenizer,
            max_length=400
        )
        log_message("Translation model and tokenizer loaded successfully.")
    except Exception as e:
        log_message(f"Error loading Transformers model: {e}")
        raise RuntimeError(f"Error loading Transformers model: {e}")

    return lang_model, translation_pipeline


# Detect the language of text
def detect_language(text, lang_model):
    try:
        prediction = lang_model.predict(text.strip().replace("\n", ""))
        log_message(f"Detected language: {prediction[0][0]} with confidence: {prediction[1][0]}")
        return prediction[0][0].replace("__label__", ""), prediction[1][0]
    except Exception as e:
        log_message(f"Language detection failed: {e}")
        raise RuntimeError(f"Language detection failed: {e}")


# Extract text based on file type
def extract_text(file_path):
    try:
        log_message(f"Extracting text from file: {file_path}")
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".pdf":
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            log_message("Text extracted from PDF successfully.")
            return text
        elif file_extension == ".txt":
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read().strip()
                log_message("Text extracted from TXT file successfully.")
                return text
        elif file_extension == ".json":
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                text = data.get("text", "")
                log_message("Text extracted from JSON file successfully.")
                return text
        else:
            log_message("Unsupported file type.")
            return None
    except Exception as e:
        log_message(f"Error extracting text: {e}")
        raise RuntimeError(f"Error extracting text: {e}")


# Translate file content
def translate_file(file_path, lang_model, translation_pipeline, target_language):
    log_message(f"Starting translation for file: {file_path}")
    text = extract_text(file_path)
    if not text:
        return {"status": "error", "message": "No valid text extracted from the file."}

    segments = text.split("\n")
    translated_segments = []
    log_entries = []

    for segment in segments:
        if not segment.strip():
            continue

        detected_language, confidence = detect_language(segment, lang_model)
        log_entries.append(
            {"segment": segment, "detected_language": detected_language, "confidence": confidence}
        )

        try:
            output = translation_pipeline(
                segment,
                src_lang=detected_language,
                tgt_lang=target_language
            )
            translated_text = output[0]['translation_text']
            translated_segments.append({"original": segment, "translated": translated_text})
            log_message(f"Segment translated successfully: {segment} -> {translated_text}")
        except Exception as e:
            log_message(f"Error translating segment: {segment}. Error: {e}")
            translated_segments.append({"original": segment, "translated": None, "error": str(e)})

    log_message(f"Translation completed for file: {file_path}")
    return {
        "status": "success",
        "original_text": text,
        "translated_text": "\n".join([t["translated"] or "" for t in translated_segments]),
        "details": translated_segments,
        "log": log_entries
    }
