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

import MeCab

# Initialize MeCab with the IPADIC dictionary
mecab = MeCab.Tagger("-Ochasen")

# Load text from a file (assuming your file is named 'japanese_text.txt')
with open('japanese_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Tokenize the text using MeCab
def tokenize_text(text):
    node = mecab.parseToNode(text)
    tokens = []
    while node:
        surface = node.surface  # The token itself
        feature = node.feature.split(',')  # POS tagging and dictionary info
        tokens.append((surface, feature))
        node = node.next
    return tokens

# Function to print the tokens
def print_tokens(tokens):
    print("Tokenized Text:")
    for token, feature in tokens:
        print(f"Surface: {token}, POS: {feature[0]}, Base Form: {feature[6]}")

# Function to find and print dates in the tokenized text
def find_date(tokens):
    print("\nQuestion: 有効期限はいつですか？ (What is the expiration date?)")
    found_dates = []
    for token, feature in tokens:
        if "名詞" in feature[0] and ("年" in token or "月" in token or "日" in token):
            found_dates.append(token)
    if found_dates:
        print(f"Found Date: {' '.join(found_dates)}")
    else:
        print("No date found.")

# Function to find and print address-related tokens
def find_address(tokens):
    print("\nQuestion: 住所はどこですか？ (What is the address?)")
    found_address = []
    for token, feature in tokens:
        if "名詞" in feature[0] and ("県" in token or "市" in token or "番地" in token):
            found_address.append(token)
    if found_address:
        print(f"Found Address: {' '.join(found_address)}")
    else:
        print("No address found.")

# Function to find and print numeric tokens (useful for IDs, numbers, etc.)
def find_numbers(tokens):
    print("\nQuestion: 番号は何ですか？ (What is the number?)")
    found_numbers = []
    for token, feature in tokens:
        if feature[0] == "名詞" and token.isdigit():
            found_numbers.append(token)
    if found_numbers:
        print(f"Found Numbers: {' '.join(found_numbers)}")
    else:
        print("No numbers found.")

# Tokenize and process the text
tokens = tokenize_text(text)

# Print the tokenized output
print_tokens(tokens)

# Ask and answer specific questions
find_date(tokens)
find_address(tokens)
find_numbers(tokens)
