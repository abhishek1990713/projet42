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
from lang import LanguageDetectionService  # Assuming this is a custom module

# Step 1: Load FastText model for language detection
pretrained_lang_model = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
model = fasttext.load_model(pretrained_lang_model)

# Step 2: Language detection from input text
text = "صباح الخير، الجو جميل اليوم والسماء صافية"  # Example Arabic text
lang_detector = LanguageDetectionService(text)
detected_language = lang_detector.main()  # Detected language code (e.g., 'ar' for Arabic)
print("Detected Language:", detected_language)

# Step 3: Supported language codes and their names
language_codes = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German', 'it': 'Italian', 'ar': 'Arabic',
    'pt': 'Portuguese', 'zh': 'Chinese', 'ja': 'Japanese', 'ru': 'Russian', 'hi': 'Hindi',
    'ko': 'Korean', 'nl': 'Dutch', 'tr': 'Turkish', 'pl': 'Polish', 'sv': 'Swedish', 'ro': 'Romanian',
    'bn': 'Bengali', 'ta': 'Tamil', 'mr': 'Marathi', 'te': 'Telugu', 'th': 'Thai', 'id': 'Indonesian',
    'vi': 'Vietnamese', 'cs': 'Czech', 'uk': 'Ukrainian', 'el': 'Greek', 'he': 'Hebrew', 'sr': 'Serbian'
}

# Display available languages and their codes
print("\nAvailable languages:")
for code, language in language_codes.items():
    print(f"{code}: {language}")

# Step 4: User input for target language code
target_language = input("\nEnter target language code (e.g., 'es' for Spanish): ").strip()

# Validate input language code
if target_language not in language_codes:
    print("Invalid language code. Please choose from the available options.")
    exit(1)

# Step 5: Load translation model and tokenizer
checkpoint = r"C:\CitiDev\language_prediction\m2m"
model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Step 6: Setup translation pipeline
translation_pipeline = pipeline('translation', model=model, tokenizer=tokenizer, max_length=400)

# Step 7: Translate the text based on detected source language and user-provided target language
output = translation_pipeline(text, src_lang=detected_language, tgt_lang=target_language)
print("\nTranslated Text:", output[0]['translation_text'])
