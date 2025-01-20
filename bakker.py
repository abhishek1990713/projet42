import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Step 1: Language Detection
def detect_language(text, fasttext_model_path):
    model = fasttext.load_model(fasttext_model_path)
    predictions = model.predict(text, k=1)
    input_lang = predictions[0][0].replace("__label__", "")
    return input_lang

# Step 2: Map Detected Language to NLLB Code
def map_language(input_lang, lang_mapping):
    return lang_mapping.get(input_lang, None)

# Step 3: Translation Pipeline Setup
def setup_translation_pipeline(checkpoint, src_lang, tgt_lang):
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
    return pipeline(
        "translation",
        model=model,
        tokenizer=tokenizer,
        src_lang=src_lang,
        tgt_lang=tgt_lang,
        max_length=400
    )

# Step 4: Perform Translation
def translate_text(translation_pipeline, text):
    try:
        output = translation_pipeline(text)
        if output:
            return output[0]["translation_text"]
        else:
            print("Translation pipeline returned empty output.")
            return None
    except Exception as e:
        print(f"Error during translation: {e}")
        return None

# Language Mapping Dictionary
lang_mapping = {
    "ar": "arb_Arab", "en": "eng_Latn", "es": "spa_Latn", "fr": "fra_Latn", 
    "de": "deu_Latn", "hi": "hin_Deva", "zh": "zho_Hans", "ja": "jpn_Jpan"  # Added Japanese
}

# Inputs
fasttext_model_path = "/path/to/lid.176.bin"  # Update with your path
nllb_checkpoint = "facebook/nllb-200-1.3B"
text = "おはようございます、今日は天気が良いです。"  # Japanese text
target_lang = "eng_Latn"  # English

# Workflow
print("Step 1: Detecting Language...")
detected_lang = detect_language(text, fasttext_model_path)
print(f"Detected Language (FastText): {detected_lang}")

print("\nStep 2: Mapping Language Code...")
mapped_lang = map_language(detected_lang, lang_mapping)
if not mapped_lang:
    print("Error: Detected language is not supported by NLLB.")
else:
    print(f"Mapped Language (NLLB): {mapped_lang}")

    print("\nStep 3: Setting up Translation Pipeline...")
    translation_pipeline = setup_translation_pipeline(nllb_checkpoint, mapped_lang, target_lang)

    print("\nStep 4: Performing Translation...")
    translated_text = translate_text(translation_pipeline, text)
    if translated_text:
        print(f"Translated Text: {translated_text}")
    else:
        print("Error: No translated text received.")
