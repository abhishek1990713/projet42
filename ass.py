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

from sudachipy import tokenizer
from sudachipy import dictionary

# Initialize the SudachiPy tokenizer
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C

# Load text from a file (assuming your file is named 'japanese_text.txt')
with open('japanese_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Tokenize the text using SudachiPy
tokens = tokenizer_obj.tokenize(text, mode)

# Function to print the tokens
def print_tokens(tokens):
    print("Tokenized Text:")
    for token in tokens:
        print(f"Surface: {token.surface()}, Dictionary Form: {token.dictionary_form()}, Reading: {token.reading_form()}")

# Function to find and print dates in the tokenized text
def find_date(tokens):
    print("\nQuestion: 有効期限はいつですか？ (What is the expiration date?)")
    found_dates = []
    for token in tokens:
        if "年" in token.surface() or "月" in token.surface() or "日" in token.surface():
            found_dates.append(token.surface())
    if found_dates:
        print(f"Found Date: {' '.join(found_dates)}")
    else:
        print("No date found.")

# Function to find and print address-related tokens
def find_address(tokens):
    print("\nQuestion: 住所はどこですか？ (What is the address?)")
    found_address = []
    for token in tokens:
        if "県" in token.surface() or "市" in token.surface() or "番地" in token.surface():
            found_address.append(token.surface())
    if found_address:
        print(f"Found Address: {' '.join(found_address)}")
    else:
        print("No address found.")

# Function to find and print numeric tokens (useful for ID, numbers, etc.)
def find_numbers(tokens):
    print("\nQuestion: 番号は何ですか？ (What is the number?)")
    found_numbers = []
    for token in tokens:
        if token.surface().isdigit():
            found_numbers.append(token.surface())
    if found_numbers:
        print(f"Found Numbers: {' '.join(found_numbers)}")
    else:
        print("No numbers found.")

# Print the tokenized output
print_tokens(tokens)

# Ask and answer specific questions
find_date(tokens)
find_address(tokens)
find_numbers(tokens)

