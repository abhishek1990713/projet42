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

from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

# Specify paths
model_path = '/content/drive/MyDrive/qa/models'
tokenizer_path = '/content/drive/MyDrive/qa/tokenizer'
#context_file_path = '/content/drive/MyDrive/qa/context.txt'  # Path to your text file

# Load model and tokenizer
model = AutoModelForQuestionAnswering.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)


# Create the question-answering pipeline
nlp = pipeline('question-answering', model=model, tokenizer=tokenizer)

# Input for question-answering
QA_input = {
    'question': 'Why is model conversion important?',
    'context': 'context'
}

# Get predictions
res = nlp(QA_input)
print(res)
