from flask import Flask, jsonify, request
import ssl
import fasttext

import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import logging

# Configure logging
logging.basicConfig(
    filename="translation_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger()

def initialize_models(lang_model_path, translation_model_path):
    """Initialize the FastText and translation models."""
    logger.info("Initializing translation models...")
    try:
        # Load the language detection model
        lang_model = fasttext.load_model(lang_model_path)
        logger.info("Language model loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading FastText model: {e}")
        raise RuntimeError(f"Error loading FastText model: {e}")

    try:
        # Load the translation model and tokenizer
        translation_model = AutoModelForSeq2SeqLM.from_pretrained(translation_model_path)
        tokenizer = AutoTokenizer.from_pretrained(translation_model_path)
        translation_pipeline = pipeline(
            'translation',
            model=translation_model,
            tokenizer=tokenizer,
            max_length=400
        )
        logger.info("Translation model loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading translation model: {e}")
        raise RuntimeError(f"Error loading translation model: {e}")

    return lang_model, translation_pipeline

def detect_language(text, lang_model):
    """Detect the language of the given text."""
    try:
        # Predict language using the FastText model
        prediction = lang_model.predict(text.strip().replace("\n", ""))
        detected_language = prediction[0][0].replace("__label__", "")
        confidence = prediction[1][0]
        logger.info(f"Detected language: {detected_language} with confidence: {confidence}")
        return detected_language, confidence
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise RuntimeError(f"Language detection failed: {e}")

def translate_segment(segment, lang_model, translation_pipeline, target_language="en"):
    """Translate a single segment of text."""
    try:
        if not segment.strip():
            return None  # Skip empty segments

        # Detect language of the segment
        detected_language, confidence = detect_language(segment, lang_model)

        # Translate the text using the translation pipeline
        output = translation_pipeline(segment, src_lang=detected_language, tgt_lang=target_language)
        translated_text = output[0]["translation_text"]

        logger.info(f"Translated: {segment} -> {translated_text}")
        return translated_text
    except Exception as e:
        logger.error(f"Error translating segment: {segment}. Error: {e}")
        return f"Error: {str(e)}"

def translate_details(details, lang_model, translation_pipeline, target_language="en"):
    """Translate a list of text details segment-wise."""
    translated_details = []

    for detail in details:
        translated_text = translate_segment(detail, lang_model, translation_pipeline, target_language)
        translated_details.append({
            "original": detail,
            "translated": translated_text
        })

    return translated_details

# Example usage
if __name__ == "__main__":
    # Define paths for the language detection and translation models
    lang_model_path = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
    translation_model_path = r"C:\CitiDev\language_prediction\m2m"

    # Initialize the models
    lang_model, translation_pipeline = initialize_models(lang_model_path, translation_model_path)

    # Example details for translation
    details = [
        "Detected Label: Expiration date: 2024年(令和06年) 06月01日まで有効",
        "Extracted Year: 2024",
        "Year 2024 is within the valid range (2024-2032).",
        "Detected Label: Name: 曾国置本露花子",
        "Detected Label: Address: ヨメカ関島",
        "Detected Label: DOB: 昭和61年 5月1日生"
    ]

    # Translate the details segment-wise
    translated_details = translate_details(details, lang_model, translation_pipeline, target_language="en")

    # Print translated details
    print("Translated Details:")
    for entry in translated_details:
        print(f"Original: {entry['original']}")
        print(f"Translated: {entry['translated']}")
        print()
