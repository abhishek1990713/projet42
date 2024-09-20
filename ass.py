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

import gensim
import numpy as np

# Load your pre-trained Word2Vec model
model_path = 'path/to/your/word2vec/model'
model = gensim.models.KeyedVectors.load_word2vec_format(model_path, binary=True)

# Read text from the .txt file
with open('path/to/your/textfile.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# Tokenize the text into words
words = text.split()

# Generate embeddings for each word
embeddings = []
for word in words:
    if word in model:
        embeddings.append(model[word])

# If you need a single vector for the entire text, you can average the word vectors
if embeddings:
    text_embedding = np.mean(embeddings, axis=0)
else:
    text_embedding = None  # Handle case where no words are in the model

print(text_embedding)

