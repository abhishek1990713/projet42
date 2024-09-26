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

# Initialize MeCab
mecab = MeCab.Tagger()

# Load text from a file (assuming your file is named 'text_input.txt')
with open('text_input.txt', 'r', encoding='utf-8') as f:
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

# Function to extract all nouns and their associated information
def extract_nouns(tokens):
    nouns = []
    for token, feature in tokens:
        if "名詞" in feature[0]:  # Check if the token is a noun
            nouns.append(token)
    return nouns

# Function to respond to user questions
def respond_to_question(question, nouns):
    # Check if any noun is mentioned in the question
    relevant_nouns = [noun for noun in nouns if noun in question]
    
    if relevant_nouns:
        print(f"Found relevant information: {' '.join(relevant_nouns)}")
    else:
        print("No relevant information found.")

# Tokenize the text
tokens = tokenize_text(text)

# Print the tokenized output
print_tokens(tokens)

# Extract nouns from the tokens
nouns = extract_nouns(tokens)

# User interaction loop
while True:
    question = input("\n何か質問がありますか？ (Do you have any questions? Type 'exit' to quit): ")
    if question.lower() == 'exit':
        break
    respond_to_question(question, nouns)
