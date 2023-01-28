from __future__ import division, print_function
import json
import sys
import os
import glob
import moviepy.editor as mp
import ffmpeg
import re
import numpy as np
import librosa
#import pandas as pd
# Flask utils
from flask import Flask, redirect, url_for, request, render_template, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from moviepy.editor import concatenate_audioclips, AudioFileClip
import pydub
# Define a flask app
app = Flask(__name__)
CORS(app)

data_path = "saved_models/best13.json"
with open(data_path, "r") as fp:
    data = json.load(fp)

y = np.array(data["mapping"])
le = LabelEncoder()
le.fit_transform(y)



SAMPLES_TO_CONSIDER = 22050


#print('Model loaded. Check http://127.0.0.1:5000/')
SAMPLES_TO_CONSIDER = 22050

MODEL_PATH = 'saved_models/best13.h5'

# Load your trained model
model_lstm = tf.keras.models.load_model(MODEL_PATH)




def model_predict( audio_path,num_mfcc=13, n_fft=2048, hop_length=512):

    # load audio file
    signal, sample_rate = librosa.load(audio_path)


    if len(signal) >= SAMPLES_TO_CONSIDER:
        # ensure consistency of the length of the signal
        signal = signal[:SAMPLES_TO_CONSIDER]

        # extract MFCCs
        MFCCs = librosa.feature.mfcc(signal, sample_rate, n_mfcc=num_mfcc, n_fft=n_fft,
                                     hop_length=hop_length)
        MFCCs = MFCCs[np.newaxis, ..., np.newaxis]
        feature_scaled = np.mean(MFCCs.T, axis=0)

        return np.array([feature_scaled])

    #return preds


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index4.html')


@app.route('/predict', methods=['GET', 'POST'])
def Upload():
    if request.method == 'GET':
        files = glob.glob('uploads' + "/*")
        print(files)
        length = len(files)
        print(length)
        data_path = "saved_models/best13.json"
        with open(data_path, "r") as fp:
            data = json.load(fp)

        abcd = np.array(data["labels" ][0])



        for i in range(length):
            prediction_feature = model_predict((files[i]))
            print(files[i])
            predicted_vector = np.argmax(model_lstm.predict(prediction_feature), axis=-1)
            if predicted_vector == abcd:
                predicted_class = le.inverse_transform(predicted_vector)
                result = predicted_class[0]
                name = str(result)
                # result = result + '.wav'
                # lst1 = audio_path( '/')
                print(name)



            else:
                wav_file = pydub.AudioSegment.from_file(file=files[i],
                                                        format="wav")
                # Increase the volume by 10 dB
                new_wav_file = wav_file + 10

                # Reducing volume by 5
                silent_wav_file = wav_file - 100

                silent_wav_file.export(out_f=files[i],
                                       format="wav")
        files = glob.glob('uploads' + "/*")
        print(files)
        length = len(files)
        print(length)
        array = []
        for i in range(length):
            prediction_feature = AudioFileClip((files[i]))
            array.append(prediction_feature)
        final_audio = concatenate_audioclips(array)
        final_audio.write_audiofile("output/output.wav")

        for j in range(length):
            os.remove((files[j]))





        return str(result)
    return None

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)