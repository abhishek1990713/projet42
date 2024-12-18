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

# Step 1: Load the FastText model for language identification
pretrained_lang_model = "/content/lid218e.bin"  # path to the pretrained language model file
model = fasttext.load_model(pretrained_lang_model)

# Step 2: Language identification
text = "صباح الخير، الجو جميل اليوم والسماء صافية."  # example text
predictions = model.predict(text, k=1)
input_lang = predictions[0][0].replace('__label__', '')  # Extract detected language

# Step 3: Load the translation model and tokenizer
checkpoint = "Helsinki-NLP/opus-mt-ar-es"  # Example checkpoint for Arabic to Spanish
model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Step 4: Setup translation pipeline
translation_pipeline = pipeline('translation_ar_to_es',  # You can adjust the pipeline name based on your source and target languages
                                model=model, 
                                tokenizer=tokenizer, 
                                max_length=400)

# Step 5: Translate the text
output = translation_pipeline(text)
print("Translated Text:", output[0]['translation_text'])
