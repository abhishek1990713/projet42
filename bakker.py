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
        lang_model = fasttext.load_model(lang_model_path)
        logger.info("Language model loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading FastText model: {e}")
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
        logger.info("Translation model loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading translation model: {e}")
        raise RuntimeError(f"Error loading translation model: {e}")

    return lang_model, translation_pipeline

def detect_language(text, lang_model):
    """Detect the language of the given text."""
    try:
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
        try:
            detected_language, confidence = detect_language(detail, lang_model)
            output = translation_pipeline(detail, src_lang=detected_language, tgt_lang=target_language)
            translated_text = output[0]["translation_text"]
            logger.info(f"Translated: {detail} -> {translated_text}")
            translated_details.append(translated_text)
        except Exception as e:
            logger.error(f"Error translating detail: {detail}. Error: {e}")
            translated_details.append(f"Error: {str(e)}")
    return translated_details
