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

from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch

# Specify paths
model_path = '/content/drive/MyDrive/qa/models'
tokenizer_path = '/content/drive/MyDrive/qa/tokenizer'
context_file_path = '/content/drive/MyDrive/qa/context.txt'  # Path to your Japanese text file

# Load model and tokenizer
model = AutoModelForQuestionAnswering.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

# Read the context from the .txt file (which contains Japanese text)
with open(context_file_path, 'r', encoding='utf-8') as file:
    context = file.read()

# List of questions in Japanese
questions = [
    "この文書の日付は何ですか？",  # What is the date on this document?
    "有効期限はいつですか？",       # When is the expiration date?
    "免許番号は何ですか？",         # What is the license number?
    "住所はどこですか？",           # What is the address?
    "車についての情報はありますか？", # Is there information about the car?
    "眼鏡等の記載はありますか？"     # Is there any mention of glasses?
]

# Iterate over each question, get the answer, and print both
for question in questions:
    # Tokenize input
    inputs = tokenizer(question, context, return_tensors='pt')

    # Get model output
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract the start and end logits
    start_logits = outputs.start_logits
    end_logits = outputs.end_logits

    # Get the most likely start and end token positions
    start_position = torch.argmax(start_logits)
    end_position = torch.argmax(end_logits)

    # Convert token IDs to the actual answer
    answer_tokens = inputs.input_ids[0][start_position:end_position + 1]
    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)

    # Print the question and answer
    print(f"Question: {question}")
    print(f"Answer: {answer}\n")
