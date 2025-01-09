from flask import Flask, jsonify, request
import ssl

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

def translate_text(details, lang_model, translation_pipeline, target_language="en"):
    """Translate a list of text segments to the target language."""
    translated_details = []
    
    for detail in details:
        if not detail.strip():  # Skip empty or invalid details
            continue
        try:
            # Detect language of the segment
            detected_language, confidence = detect_language(detail, lang_model)
            
            # Translate the text using the translation pipeline
            output = translation_pipeline(detail, src_lang=detected_language, tgt_lang=target_language)
            translated_text = output[0]["translation_text"]
            
            # Log the successful translation
            logger.info(f"Translated: {detail} -> {translated_text}")
            translated_details.append(translated_text)
        except Exception as e:
            # Log errors for translation failures
            logger.error(f"Error translating detail: {detail}. Error: {e}")
            translated_details.append(f"Error: {str(e)}")
    
    return translated_details

# Example of usage
if __name__ == "__main__":
    # Define paths for the language detection and translation models
    lang_model_path = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
    translation_model_path = r"C:\CitiDev\language_prediction\m2m"

    # Initialize the models
    lang_model, translation_pipeline = initialize_models(lang_model_path, translation_model_path)

    # Example text for translation
    details = [
        "Detected Label: Expiration date: 2024年(令和06年) 06月01日まで有効",
        "Extracted Year: 2024",
        "Year 2024 is within the valid range (2024-2032).",
        "Detected Label: Name: 曾国置本露花子",
        "Detected Label: Address: ヨメカ関島",
        "Detected Label: DOB: 昭和61年 5月1日生"
    ]

    # Translate the details to English
    translated_details = translate_text(details, lang_model, translation_pipeline, target_language="en")
    
    # Print the translated details
    print("Translated Details:")
    for original, translated in zip(details, translated_details):
        print(f"{original} -> {translated}")
