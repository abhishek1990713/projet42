
import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import logging
import re

# Configure logging
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

def initialize_models(lang_model_path, translation_model_path):
    """Initialize language detection and translation models."""
    log_message("Initializing models...")
    try:
        # Load language detection model
        lang_model = fasttext.load_model(lang_model_path)
        log_message("Language model loaded successfully.")
    except Exception as e:
        log_message(f"Error loading FastText model: {e}")
        raise RuntimeError(f"Error loading FastText model: {e}")

    try:
        # Load translation model and tokenizer
        translation_model = AutoModelForSeq2SeqLM.from_pretrained(translation_model_path)
        tokenizer = AutoTokenizer.from_pretrained(translation_model_path)
        translation_pipeline = pipeline(
            "translation",
            model=translation_model,
            tokenizer=tokenizer,
            max_length=400,
        )
        log_message("Translation model and tokenizer loaded successfully.")
    except Exception as e:
        log_message(f"Error loading Transformers model: {e}")
        raise RuntimeError(f"Error loading Transformers model: {e}")

    return lang_model, translation_pipeline

def detect_language(text, lang_model):
    """Detect the language of a given text."""
    try:
        prediction = lang_model.predict(text.strip().replace("\n", ""))
        log_message(f"Detected language: {prediction[0][0]} with confidence: {prediction[1][0]}")
        return prediction[0][0].replace("__label__", ""), prediction[1][0]
    except Exception as e:
        log_message(f"Language detection failed: {e}")
        raise RuntimeError(f"Language detection failed: {e}")

def translate_text(details, lang_model, translation_pipeline, target_language="en"):
    """Translate a list of text segments to the target language."""
    translated_details = []
    
    # Process each field (like DOB and Expiration date)
    for detail in details:
        try:
            detected_language, confidence = detect_language(detail, lang_model)
            
            # Handle special case for dates - don't translate year part
            if "年" in detail:  # Handles Japanese year pattern (e.g., 2024年)
                # Preserve the year part for future translation
                year_pattern = re.search(r"\d{4}年", detail)
                if year_pattern:
                    preserved_year = year_pattern.group(0)
                    detail = detail.replace(preserved_year, "<YEAR>")  # Temporarily replace year with a placeholder

            # Translate using the pipeline
            output = translation_pipeline(detail, src_lang=detected_language, tgt_lang=target_language)
            translated_text = output[0]["translation_text"]
            
            # Restore the preserved year after translation
            if "年" in translated_text:
                translated_text = translated_text.replace("<YEAR>", preserved_year)
            
            log_message(f"Translated: {detail} -> {translated_text}")
            translated_details.append(translated_text)
        except Exception as e:
            log_message(f"Error translating detail: {detail}. Error: {e}")
            translated_details.append(f"Error: {str(e)}")

    return translated_details

