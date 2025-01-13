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

# Translate word by word
def translate_word_by_word(segment, lang_model, translation_pipeline, target_language):
    words = segment.split()  # Split segment into words
    translated_words = []
    log_message(f"Translating segment word by word: {segment}")

    for word in words:
        try:
            detected_language, confidence = detect_language(word, lang_model)
            output = translation_pipeline(
                word,
                src_lang=detected_language,
                tgt_lang=target_language
            )
            translated_word = output[0]['translation_text']
            translated_words.append(translated_word)
            log_message(f"Word translated: {word} -> {translated_word}")
        except Exception as e:
            log_message(f"Error translating word: {word}. Error: {e}")
            translated_words.append(f"[Error: {word}]")

    return " ".join(translated_words)

# Translate text
def translate_text_word_by_word(input_segments, lang_model, translation_pipeline, target_language):
    log_message("Starting word-by-word translation for input text...")
    translated_segments = []

    for segment in input_segments:
        if not segment.strip():
            continue
        translated_text = translate_word_by_word(segment, lang_model, translation_pipeline, target_language)
        translated_segments.append({
            "original": segment,
            "translated": translated_text
        })

    log_message("Word-by-word translation completed.")
    return translated_segments

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

# Translate input word by word
output = translate_text_word_by_word(input_text_segments, lang_model, translation_pipeline, target_language="en")

# Print output
print(json.dumps(output, indent=4, ensure_ascii=False))
