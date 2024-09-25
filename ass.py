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

questions = [
    "この年号は何年ですか？",         # What year is "昭和50"?
    "日付はいつですか？",            # What is the date (06月03日)?
    "住所はどこですか？",            # What is the address (重県津市垂水2566番地)?
    "有効期限はいつですか？",         # When is the expiration date (平成24年07月01日まで有効)?
    "免許番号は何ですか？",           # What is the license number (23456789000)?
    "車に関する情報はありますか？",   # Is there any information about the car?
    "眼鏡等について何か記載がありますか？"  # Is there any mention of glasses?
]
