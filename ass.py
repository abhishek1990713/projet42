from flask import Flask, redirect, url_for, request, render_template, jsonify
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
from flask_cors import CORS, cross_origin
import boto3
import glob

app = Flask(__name__)

CORS(app)


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index4.html')


@app.route('/predict', methods=['GET'])
def Upload():
    if request.method == 'GET':
        # print(request.json['file'])


        r = sr.Recognizer()

        sound = AudioSegment.from_wav("inp/splite.wav")

        audio_chunks = split_on_silence(sound, min_silence_len=1000, silence_thresh=sound.dBFS - 14, keep_silence=500)
        whole_text = ""
        textMap = {}
        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join('InputFiles', f"speech_chunk{i}.wav")
            print("Exporting file", output_file)
            result = chunk.export(output_file, format="wav")




        # os.remove("inp/splite.wav")
        return str(result)

    # return str(result)
    return None
import fasttext
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import torch

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Class for Language Codes
class LanguageCodes:
    LANG_CODES = {
        "English": "eng_Latn",
        "Japanese": "jpn_Jpan",
        # Add more languages here as needed
        "Hindi": "hin_Deva",
        "Spanish": "spa_Latn",
        "French": "fra_Latn",
        "Chinese_Simplified": "zho_Hans",
        "Chinese_Traditional": "zho_Hant",
        "German": "deu_Latn",
    }

    @classmethod
    def get_lang_code(cls, language_name):
        return cls.LANG_CODES.get(language_name, None)

# Load the language identification model
def load_lang_model():
    try:
        model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
        lang_model = fasttext.load_model(model_path)
        return lang_model
    except Exception as e:
        raise Exception(f"Error loading language model: {str(e)}")

# Load the translation model and tokenizer
def load_translation_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-1.3B")
        translation_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-1.3B").to(device)
        return translation_model, tokenizer
    except Exception as e:
        raise Exception(f"Error loading translation model: {str(e)}")

# Translation function
def translate_text(input_text, source_lang, target_lang, translation_model, tokenizer):
    try:
        # Use HuggingFace pipeline for translation
        translator = pipeline(
            "translation",
            model=translation_model,
            tokenizer=tokenizer,
            src_lang=source_lang,
            tgt_lang=target_lang,
            max_length=6000,
        )
        translated_text = translator(input_text)[0]['translation_text']
        return translated_text
    except Exception as e:
        raise Exception(f"Translation error: {str(e)}")

# Main function to handle translation
def translate_sentence(input_sentence, target_language):
    try:
        # Load models
        lang_model = load_lang_model()
        translation_model, tokenizer = load_translation_model()

        # Detect source language
        lang_prediction = lang_model.predict(input_sentence)
        source_lang = lang_prediction[0][0].replace("__label__", "")

        # Get target language code
        target_lang_code = LanguageCodes.get_lang_code(target_language)
        if not target_lang_code:
            raise ValueError(f"Unsupported target language: {target_language}")

        # Translate the sentence
        translated_text = translate_text(input_sentence, source_lang, target_lang_code, translation_model, tokenizer)

        # Print the translated text
        print(f"Original: {input_sentence}")
        print(f"Translated: {translated_text}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage
if __name__ == "__main__":
    input_sentence = "Hello, how are you today?"  # Small sentence in English
    target_language = "Japanese"  # Target language is Japanese
    translate_sentence(input_sentence, target_language)
