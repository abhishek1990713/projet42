import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import logging
import json

# Configure logging
LOG_FILE = "translation_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def log_message(message):
    logging.info(message)

# Initialize models
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
            "translation",
            model=translation_model,
            tokenizer=tokenizer,
            max_length=400
        )
        log_message("Translation model and tokenizer loaded successfully.")
    except Exception as e:
        log_message(f"Error loading Transformers model: {e}")
        raise RuntimeError(f"Error loading Transformers model: {e}")

    return lang_model, translation_pipeline

# Detect language
def detect_language(text, lang_model):
    try:
        prediction = lang_model.predict(text.strip())
        detected_language = prediction[0][0].replace("__label__", "")
        confidence = prediction[1][0]
        log_message(f"Detected language: {detected_language} with confidence: {confidence}")
        return detected_language, confidence
    except Exception as e:
        log_message(f"Language detection failed: {e}")
        raise RuntimeError(f"Language detection failed: {e}")

# Translate text
def translate_text(input_segments, lang_model, translation_pipeline, target_language):
    log_message("Starting translation for input text...")
    translated_segments = []
    log_entries = []

    for segment in input_segments:
        if not segment.strip():
            continue

        detected_language, confidence = detect_language(segment, lang_model)
        log_entries.append({
            "segment": segment,
            "detected_language": detected_language,
            "confidence": confidence
        })

        try:
            output = translation_pipeline(segment, src_lang=detected_language, tgt_lang=target_language)
            translated_text = output[0]['translation_text']
            translated_segments.append({
                "original": segment,
                "translated": translated_text
            })
            log_message(f"Segment translated successfully: {segment} -> {translated_text}")
        except Exception as e:
            log_message(f"Error translating segment: {segment}. Error: {e}")
            translated_segments.append({
                "original": segment,
                "translated": None,
                "error": str(e)
            })

    log_message("Translation completed for input text.")
    return {
        "status": "success",
        "translated_segments": translated_segments,
        "log": log_entries
    }

# Direct input
input_text_segments = [
    "Detected Label: Expiration date: 2024年(令和96年) 06月01日まで有効。",
    "Extracted Year: 2024",
    "Year 2024 is within the valid range (2024-2032).",
    "Detected Label: Name: 會国置本露花子",
    "Detected Label: Address: ヨメカ関島",
    "Detected Label: DOB: 昭和61年5月1日生"
]

# Define paths
lang_model_path = r"C:\CitiDev\language_prediction\amz12\11d.176.bin"
translation_model_path = r"C:\CitiDev\language_prediction\m2m"

# Initialize models
lang_model, translation_pipeline = initialize_models(lang_model_path, translation_model_path)

# Translate input
output = translate_text(input_text_segments, lang_model, translation_pipeline, target_language="en")

# Print output
print(json.dumps(output, indent=4, ensure_ascii=False))
