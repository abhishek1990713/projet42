from __future__ import division, print_function
import json
import sys
import os
import glob
import re
import numpy as np
import librosa
import ffmpeg
# import pandas as pd
# Flask utils
from flask import Flask, redirect, url_for, request, render_template, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
import pydub
from moviepy.editor import concatenate_audioclips, AudioFileClip
import boto3

# Define a flask app
app = Flask(__name__)
CORS(app)

SAMPLES_TO_CONSIDER = 22050

# print('Model loaded. Check http://127.0.0.1:5000/')
SAMPLES_TO_CONSIDER = 22050


def model_predict(audio_path, num_mfcc=13, n_fft=2048, hop_length=512):
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

    # return preds


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index4.html')


@app.route('/predict', methods=['POST'])
def Upload():
    if request.method == 'POST':


        def download_all_objects_in_folder(xyz):

            print(xyz)
            print("location ")
            _BUCKET_NAME = 'sbr-project-2021'
            _PREFIX = xyz + "/splited_audio/"

            session = boto3.Session(
                aws_access_key_id='AKIAQRGY6UM3ZUL5MUCG',
                aws_secret_access_key='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'
            )
            s3_resource = session.resource('s3')
            my_bucket = s3_resource.Bucket(_BUCKET_NAME)
            #objects = my_bucket.objects.filter(Prefix=_PREFIX)

            resource = session.resource('s3').Bucket(_BUCKET_NAME).download_file(xyz + '/models/best126.h5',
                                                                                 'modelss3/best126.h5')
            resource = session.resource('s3').Bucket(_BUCKET_NAME).download_file(xyz + '/models/best126.json',
                                                                                 'modelss3/best126.json')
            resource = session.resource('s3').Bucket(_BUCKET_NAME).download_file(xyz + '/splited_audio/chunks0.wav',
                                                                                 'InputFiles/chunks0.wav')

            resource= session.resource('s3').Bucket(_BUCKET_NAME).download_file(xyz + '/output/' + request.json['post_id'] +'finished.mp4',  'video_name/video.mp4')
            # resource= session.resource('s3').Bucket(_BUCKET_NAME).download_file(request.json['file'] + '/output/finished.mp4',  'video_name/video.mp4')
            return "audio/"

        download_all_objects_in_folder('machine learning/' + request.json['user_id'])

        data_path = "modelss3/best13.json"
        with open(data_path, "r") as fp:
            data = json.load(fp)

        y = np.asarray(data["mapping"])
        le = LabelEncoder()
        le.fit_transform(y)

        MODEL_PATH = 'modelss3/best13.h5'

        # Load your trained model
        model_lstm = tf.keras.models.load_model(MODEL_PATH)

        # audio_path = 'uploads/sanya.wav'
        # directory = 'uploads/'

        # iterate over files in
        # that directory
        files = glob.glob('InputFiles' + "/*")
        print(files)
        length = len(files)

        data_path = "modelss3/best13.json"
        with open(data_path, "r") as fp:
            data = json.load(fp)
        abcd = np.asarray(data["labels"][0])

        for i in range(length):
            prediction_feature = model_predict((files[i]))
            print(files[i])
            predicted_vector = np.argmax(model_lstm.predict(prediction_feature), axis=-1)

            if predicted_vector == abcd:
                predicted_class = le.inverse_transform(predicted_vector)
                result = predicted_class[0]
                name = str(result)
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

        files = glob.glob('InputFiles' + "/*")
        print(files)
        length = len(files)
        print(length)
        array = []
        for i in range(length):
            prediction_feature = AudioFileClip((files[i]))
            array.append(prediction_feature)
        final_audio = concatenate_audioclips(array)

        final_audio.write_audiofile("output/output.wav")

        input_video = ffmpeg.input('video_name/video.mp4')

        input_audio = ffmpeg.input('output/output.wav')

        ffmpeg.concat(input_video, input_audio, v=1, a=1).output('output/finished_video.mp4').run()

        # os.remove('output/output.wav')
        # os.remove('output/finished_video.mp4')

        _BUCKET_NAME = 'sbr-project-2021'

        session = boto3.Session(
            aws_access_key_id='AKIAQRGY6UM3ZUL5MUCG',
            aws_secret_access_key='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'
        )
        s3 = session.resource('s3')

        # s3.Bucket(_BUCKET_NAME).upload_file('output/output.wav', "machine learning/" + request.json['user_id'] + "/output_final/final.wav")
        # s3.Bucket(_BUCKET_NAME).upload_file('output/finished_video.mp4', "machine learning/" + request.json['user_id'] + "/output_final/final.mp4")
        # data = {'name':"machine learning/" + request.json['user_id'] + "/output/audo12.wav"}

        s3.Bucket(_BUCKET_NAME).upload_file('output/output.wav',
                                            "machine learning/" + request.json['user_id'] + "/output_final/" +
                                            request.json['post_id'] + "final.wav")
        s3.Bucket(_BUCKET_NAME).upload_file('output/finished_video.mp4', "machine learning/" + request.json['user_id'] + "/output_final/" + request.json['post_id'] +"final.mp4")
        data = {'name': "machine learning/" + request.json['user_id'] + "/output_final/" + request.json[
            'post_id'] + "final.wav"}

        for j in range(length):
            os.remove((files[j]))

        os.remove('output/output.wav')
        # os.remove('output/finished_video.mp4')

        return str(jsonify(data))

        # return str(result)
    return None
    # return str(length)
    # return None


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)

