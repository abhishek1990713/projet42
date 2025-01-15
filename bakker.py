import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Load the FastText pretrained language detection model
pretrained_lang_model = "/content/lid.176.bin"  # Ensure this file is downloaded
model_ft = fasttext.load_model(pretrained_lang_model)

# Text to detect and translate
text = "صباح الخير، الجو جميل اليوم والسماء صافية."

# Detect language using FastText
predictions = model_ft.predict(text, k=1)  # Top-1 prediction
input_lang = predictions[0][0].replace("__label__", "")  # Extract language code
print(f"Detected Language: {input_lang}")

# Load NLLB model and tokenizer
checkpoint = "facebook/nllb-200-1.3B"  # You can change to a different NLLB checkpoint
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model_nllb = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)

# Define target language
target_lang = "spa_Latn"  # Target language code (Spanish in Latin script)

# Create a translation pipeline
translation_pipeline = pipeline(
    "translation",
    model=model_nllb,
    tokenizer=tokenizer,
    src_lang=input_lang,
    tgt_lang=target_lang,
    max_length=400
)

# Perform translation
output = translation_pipeline(text)
print("Translated Text:", output[0]['translation_text'])
