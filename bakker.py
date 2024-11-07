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


@app.route('/predict', methods=['POST'])
def Upload():
    if request.method == 'POST':
        # print(request.json['file'])

        def download_all_objects_in_folder(xyz):
            print(xyz)
            print("location ")
            print(request.json['file'])
            _BUCKET_NAME = 'sbr-project-2021'
            _PREFIX = xyz

            session = boto3.Session(
                aws_access_key_id='AKIAQRGY6UM3ZUL5MUCG',
                aws_secret_access_key='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'
            )
            resource = session.resource('s3').Bucket(_BUCKET_NAME).download_file(xyz,
                                                                                 'inp/splite.wav')
            # s3_resource = session.resource('s3')
            # my_bucket = s3_resource.Bucket(_BUCKET_NAME)
            # resource = s3_resource.download_file(_BUCKET_NAME, request.json['file'],  'video_name/xyz.mp4')

            return None

        print(request.json['user_id'])

        download_all_objects_in_folder(
            'machine learning/' + request.json['user_id'] + '/output/' + request.json['post_id'] + 'audo12.wav')

        r = sr.Recognizer()

        sound = AudioSegment.from_wav("inp/splite.wav")

        audio_chunks = split_on_silence(sound, min_silence_len=2000, silence_thresh=sound.dBFS - 14, keep_silence=500)
        whole_text = ""
        textMap = {}
        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join('InputFiles', f"speech_chunk{i}.wav")
            print("Exporting file", output_file)
            result = chunk.export(output_file, format="wav")

        _BUCKET_NAME = 'sbr-project-2021'

        session = boto3.Session(
            aws_access_key_id='AKIAQRGY6UM3ZUL5MUCG',
            aws_secret_access_key='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'
        )
        s3 = session.resource('s3')
        files = glob.glob('InputFiles' + "/*")
        print(files)
        length = len(files)
        print(length)
        array = []
        for i in range(length):
            s3.Bucket(_BUCKET_NAME).upload_file(files[i],
                                                "machine learning/" + request.json[
                                                    'user_id'] + "/splited_audio/" + 'chunks' + str(i) + '.wav')

        data = {'name': "machine learning/" + request.json['user_id'] + "/splited_audio/"}

        os.remove("inp/splite.wav")
        return jsonify(data)

    # return str(result)
    return None


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=6000, debug=True)


import numpy as np
import warnings
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.applications.mobilenet import preprocess_input, decode_predictions

warnings.simplefilter('ignore')

# Load the MobileNet model with pre-trained ImageNet weights
model = MobileNet(weights='imagenet')
print("MobileNet model loaded with ImageNet weights.")

# Function to assess image quality (using a dummy approach here since MobileNet was not trained for blur detection)
def assess_image_quality(image_path, model):
    # Load and preprocess the image
    img = keras_image.load_img(image_path, target_size=(224, 224))
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Run the image through the model and get predictions
    predictions = model.predict(img_array)
    
    # Decode and print top predictions
    decoded_predictions = decode_predictions(predictions, top=3)[0]
    print("Top 3 Predictions:")
    for i, (imagenet_id, label, score) in enumerate(decoded_predictions):
        print(f"{i + 1}: {label} ({score:.2f})")

    # A mock quality score based on prediction confidence for this example
    mean_score = np.mean(predictions)  # This won't give actual blurriness but is a placeholder for quality
    return mean_score

# Function to determine if image is blurry (using a simple threshold)
def is_image_blurry(image_path, model, blur_threshold=0.1):
    mean_score = assess_image_quality(image_path, model)
    # This threshold would need adjustment for actual blur detection purposes
    return "Blurry" if mean_score < blur_threshold else "Sharp"

# Path to the image
image_path = r"C:\CitiDev\text_ocr\image_quality\augmented_me_images.png"

# Get result
result = is_image_blurry(image_path, model)
print(f"The image is: {result}")
