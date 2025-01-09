from flask import Flask, jsonify, request
import ssl
import fasttext

import json
import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import logging

# Configure logging with UTF-8 support
LOG_FILE = "translation_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")]
)

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
        prediction = lang_model.predict(text.strip())
        log_message(f"Detected language: {prediction[0][0]} with confidence: {prediction[1][0]}")
        return prediction[0][0].replace("__label__", ""), prediction[1][0]
    except Exception as e:
        log_message(f"Language detection failed: {e}")
        raise RuntimeError(f"Language detection failed: {e}")

# Translate details
def translate_details(details, lang_model, translation_pipeline, target_language):
    translated_segments = []
    log_entries = []

    for detail in details:
        if not detail.strip():
            continue

        detected_language, confidence = detect_language(detail, lang_model)
        log_entries.append({
            "detail": detail,
            "detected_language": detected_language,
            "confidence": confidence
        })

        try:
            output = translation_pipeline(detail, src_lang=detected_language, tgt_lang=target_language)
            translated_text = output[0]['translation_text']
            translated_segments.append({"original": detail, "translated": translated_text})
            log_message(f"Detail translated successfully: {detail} -> {translated_text}")
        except Exception as e:
            log_message(f"Error translating detail: {detail}. Error: {e}")
            translated_segments.append({"original": detail, "translated": None, "error": str(e)})

    return {
        "status": "success",
        "original_details": details,
        "translated_details": [t["translated"] or "" for t in translated_segments],
        "log": log_entries
    }

# Paths
lang_model_path = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
translation_model_path = r"C:\CitiDev\language_prediction\m2m"

# Initialize models
lang_model, translation_pipeline = initialize_models(lang_model_path, translation_model_path)

# Input details
details = [
    "Detected Label: Expiration date: 2024年(令和06年) 06月01日まで有効",
    "Extracted Year: 2024",
    "Year 2024 is within the valid range (2024-2032).",
    "Detected Label: Name: 曾国置本露花子",
    "Detected Label: Address: ヨメカ関島",
    "Detected Label: DOB: 昭和61年 5月1日生"
]

# Translate details
output = translate_details(details, lang_model, translation_pipeline, target_language="en")

# Print output
print(json.dumps(output, indent=4, ensure_ascii=False))
