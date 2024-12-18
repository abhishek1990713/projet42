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
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load pre-trained FastText model for language detection
model_path = "/content/lid218e.bin"  # path to your FastText model
lang_model = fasttext.load_model(model_path)

# LanguageDetectionService class
class LanguageDetectionService:
    def __init__(self, text: str):
        self.text = text

    def detect_language(self):
        try:
            lang_prediction = lang_model.predict(self.text)
            lang_code = lang_prediction[0][0].replace("__label__", "")
            logger.info(f"Detected language: {lang_code}")
            return lang_code
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            raise

# Translation function using HuggingFace transformers
def translate_text(text, source_lang, target_lang):
    try:
        # Load translation model and tokenizer
        checkpoint = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
        tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        
        # Setup translation pipeline
        translation_pipeline = pipeline('translation', model=model, tokenizer=tokenizer, max_length=400)
        
        # Translate the text
        output = translation_pipeline(text)
        translated_text = output[0]['translation_text']
        logger.info(f"Translated text: {translated_text}")
        return translated_text
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise

# Main function to detect language and translate
def main(text, target_lang):
    # Step 1: Detect the language
    lang_detection_service = LanguageDetectionService(text)
    source_lang = lang_detection_service.detect_language()

    # Step 2: Translate the text
    translated_text = translate_text(text, source_lang, target_lang)
    
    return translated_text

# Example usage
text = "صباح الخير، الجو جميل اليوم والسماء صافية."  # Input text
target_lang = 'es'  # Target language (Spanish)

# Translate the text
result = main(text, target_lang)
print(f"Original Text: {text}")
print(f"Translated Text: {result}")
