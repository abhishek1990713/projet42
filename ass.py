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
import numpy as np
import os
import tensorflow as tf

# Load the best weights from training
model.load_weights('best_model.h5')

# Directory where your test images are stored
test_dir = 'test_data/'  # Replace with your test image folder

# Function to preprocess and predict a single image
def predict_image(img_path, model):
    # Load image using TensorFlow
    img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
    
    # Preprocess image
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Rescale image (same as training)

    # Make prediction
    prediction = model.predict(img_array)
    
    # Interpret prediction (assuming binary classification)
    if prediction[0] > 0.5:
        print(f'{os.path.basename(img_path)}: Passport')
    else:
        print(f'{os.path.basename(img_path)}: Driving License')

# Iterate through all test images in the directory
for img_file in os.listdir(test_dir):
    img_path = os.path.join(test_dir, img_file)
    predict_image(img_path, model)
