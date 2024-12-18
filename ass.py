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
from lang import LanguageDetectionService  # Assuming this is a custom module with the defined class

# Step 1: Load the FastText model for language identification
pretrained_lang_model = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"  # path to the FastText model
model = fasttext.load_model(pretrained_lang_model)

# Step 2: Language identification
text = "صباح الخير، الجو جميل اليوم والسماء صافية"  # Example text in Arabic

# Assuming LanguageDetectionService has a method `main()` that detects the language and returns it
lang_detector = LanguageDetectionService(text)
detected_language = lang_detector.main()  # Detected language code (e.g., 'ar' for Arabic)
print("Detected Language:", detected_language)

# Step 3: User input for target language
# You can use any language code supported by the model (e.g., 'es' for Spanish, 'fr' for French)
target_language = input("Enter the target language code (e.g., 'es' for Spanish): ")

# Step 4: Load the translation model and tokenizer
checkpoint = r"C:\CitiDev\language_prediction\m2m"  # Path to M2M model or any other multilingual model
model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Step 5: Setup translation pipeline
# Here we dynamically use the source language (detected_language) and target language (user input)
translation_pipeline = pipeline('translation', model=model, tokenizer=tokenizer, max_length=400)

# Step 6: Translate the text
output = translation_pipeline(text, src_lang=detected_language, tgt_lang=target_language)
print("Translated Text:", output[0]['translation_text'])
