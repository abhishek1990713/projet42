
from fasttext import load_model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load FastText language detection model
lang_detector = load_model('lid.176.bin')  # Download 'lid.176.bin' from FastText

# Load NLLB model and tokenizer
model_name = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def detect_language(text):
    lang_prediction = lang_detector.predict(text, k=1)
    return lang_prediction[0][0].replace("__label__", "")  # Extract language code

def translate_text(text, target_lang):
    # Detect source language
    source_lang = detect_language(text)
    
    # Prepare inputs for translation
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    
    # Perform translation
    translated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id[target_lang])
    translation = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    
    return source_lang, translation

# Example usage
input_text = "Bonjour, comment ça va ?"  # Example input text
target_language = "eng"  # Target language code (e.g., "eng" for English)

source_language, translated_text = translate_text(input_text, target_language)
print(f"Source Language: {source_language}")
print(f"Translated Text: {translated_text}")
