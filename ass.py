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

# Initialize MeCab without specifying the output format
mecab = MeCab.Tagger()

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
        base_form = feature[6] if len(feature) > 6 else '*'  # Check length of feature list
        print(f"Surface: {token}, POS: {feature[0]}, Base Form: {base_form}")

# Function to find and print passport number in the tokenized text
def find_passport_number(tokens):
    print("\nQuestion: パスポート番号は何ですか？ (What is the passport number?)")
    found_number = ""
    for token, feature in tokens:
        if "名詞" in feature[0] and ("TRO" in token or "R" in token):
            found_number = token
            break
    if found_number:
        print(f"Passport Number: {found_number}")
    else:
        print("No passport number found.")

# Function to find and print dates in the tokenized text
def find_dates(tokens):
    print("\nQuestion: 発行日と有効期限はいつですか？ (What are the issue and expiration dates?)")
    issue_date = ""
    expiration_date = ""
    dates = []
    for token, feature in tokens:
        if "名詞" in feature[0] and token.isdigit():
            dates.append(token)
    
    if len(dates) >= 4:  # Assuming issue and expiration dates have year, month, and day
        issue_date = f"{dates[0]} {dates[1]} {dates[2]}"  # e.g., "02 SEP 2013"
        expiration_date = f"{dates[3]} {dates[4]} {dates[5]}"  # e.g., "02 SEP 2023"
    
    if issue_date and expiration_date:
        print(f"Issue Date: {issue_date}")
        print(f"Expiration Date: {expiration_date}")
    else:
        print("No dates found.")

# Function to find and print names (e.g., "SAKURA") in the tokenized text
def find_name(tokens):
    print("\nQuestion: 名前は何ですか？ (What is the name?)")
    name = ""
    for token, feature in tokens:
        if "名詞" in feature[0] and token.isalpha() and len(token) > 1:
            name = token
            break
    if name:
        print(f"Name: {name}")
    else:
        print("No name found.")

# Tokenize and process the text
tokens = tokenize_text(text)

# Print the tokenized output
print_tokens(tokens)

# Ask and answer specific questions
find_passport_number(tokens)
find_dates(tokens)
find_name(tokens)
