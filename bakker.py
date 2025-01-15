import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Load FastText language detection model
pretrained_lang_model = "/path/to/lid.176.bin"  # Update with your FastText model path
model_ft = fasttext.load_model(pretrained_lang_model)

# Language mapping from FastText to NLLB codes
lang_mapping = {
    "af": "afr_Latn", "am": "amh_Ethi", "ar": "arb_Arab", "az": "aze_Latn", 
    "be": "bel_Cyrl", "bg": "bul_Cyrl", "bn": "ben_Beng", "bs": "bos_Latn",
    "ca": "cat_Latn", "ceb": "ceb_Latn", "cs": "ces_Latn", "cy": "cym_Latn",
    "da": "dan_Latn", "de": "deu_Latn", "el": "ell_Grek", "en": "eng_Latn",
    "es": "spa_Latn", "et": "est_Latn", "eu": "eus_Latn", "fa": "pes_Arab",
    "fi": "fin_Latn", "fil": "fil_Latn", "fr": "fra_Latn", "ga": "gle_Latn",
    "gl": "glg_Latn", "gu": "guj_Gujr", "ha": "hau_Latn", "he": "heb_Hebr",
    "hi": "hin_Deva", "hr": "hrv_Latn", "ht": "hat_Latn", "hu": "hun_Latn",
    "hy": "hye_Armn", "id": "ind_Latn", "ig": "ibo_Latn", "is": "isl_Latn",
    "it": "ita_Latn", "ja": "jpn_Jpan", "jv": "jav_Latn", "ka": "kat_Geor",
    "kk": "kaz_Cyrl", "km": "khm_Khmr", "kn": "kan_Knda", "ko": "kor_Hang",
    "ky": "kir_Cyrl", "lb": "ltz_Latn", "lo": "lao_Laoo", "lt": "lit_Latn",
    "lv": "lav_Latn", "mg": "mlg_Latn", "mi": "mri_Latn", "mk": "mkd_Cyrl",
    "ml": "mal_Mlym", "mn": "mon_Cyrl", "mr": "mar_Deva", "ms": "zsm_Latn",
    "mt": "mlt_Latn", "my": "mya_Mymr", "ne": "npi_Deva", "nl": "nld_Latn",
    "no": "nob_Latn", "ny": "nya_Latn", "or": "ory_Orya", "pa": "pan_Guru",
    "pl": "pol_Latn", "ps": "pbt_Arab", "pt": "por_Latn", "ro": "ron_Latn",
    "ru": "rus_Cyrl", "rw": "kin_Latn", "sd": "snd_Arab", "si": "sin_Sinh",
    "sk": "slk_Latn", "sl": "slv_Latn", "sm": "smo_Latn", "sn": "sna_Latn",
    "so": "som_Latn", "sq": "als_Latn", "sr": "srp_Cyrl", "st": "sot_Latn",
    "su": "sun_Latn", "sv": "swe_Latn", "sw": "swh_Latn", "ta": "tam_Taml",
    "te": "tel_Telu", "tg": "tgk_Cyrl", "th": "tha_Thai", "tl": "tgl_Latn",
    "tr": "tur_Latn", "uk": "ukr_Cyrl", "ur": "urd_Arab", "uz": "uzb_Latn",
    "vi": "vie_Latn", "xh": "xho_Latn", "yo": "yor_Latn", "zh": "zho_Hans",
    "zu": "zul_Latn"
}

# Input text
text = "صباح الخير، الجو جميل اليوم والسماء صافية."

# Detect source language
predictions = model_ft.predict(text, k=1)
input_lang = predictions[0][0].replace("__label__", "")
print(f"Detected Language (FastText): {input_lang}")

# Map detected language to NLLB language code
input_lang = lang_mapping.get(input_lang, input_lang)
print(f"Mapped Language (NLLB): {input_lang}")

# Load NLLB model and tokenizer
checkpoint = "facebook/nllb-200-1.3B"  # Use other checkpoints if needed
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model_nllb = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)

# Define target language
target_lang = "spa_Latn"  # Translate to Spanish (Latin script)

# Create translation pipeline
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
if output:
    print("Translated Text:", output[0]['translation_text'])
else:
    print("No translation generated.")
