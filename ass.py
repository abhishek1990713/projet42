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


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=6000, debug=True)

from transformers import pipeline, BartForConditionalGeneration, BartTokenizer

# Load the saved model and tokenizer
model = BartForConditionalGeneration.from_pretrained('/content/drive/MyDrive/qa/bart-large-cnn')
tokenizer = BartTokenizer.from_pretrained('/content/drive/MyDrive/qa/bart-large-cnn')

# Create the pipeline with the locally loaded model and tokenizer
ARTICLE = """ New York (CNN)When Liana Barrientos was 23 years old, she got married..."""

# Tokenize the input text
inputs = tokenizer(ARTICLE, return_tensors="pt", max_length=1024, truncation=True)

# Generate summary IDs (with model predictions)
summary_ids = model.generate(inputs["input_ids"], max_length=130, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)

# Decode the summary
summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

print(summary)
