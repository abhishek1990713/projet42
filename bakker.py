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

import os
import numpy as np
import cv2
from keras.models import load_model
import time
from image_quality import ImageQualityAssessor  # Assuming Code 1 is saved in image_quality.py
from image_classification import ImageClassifier  # Assuming Code 2 is saved in image_classification.py

# Function to check image quality and classify if it's sharp
def process_image(image_path, quality_assessor, classifier):
    # Step 1: Check image quality
    quality_result = quality_assessor.is_image_blurry(image_path)
    
    if quality_result == "Blurry":
        print(f"The image is blurry and cannot be processed.")
        return None
    
    print(f"The image is sharp. Proceeding with classification...")

    # Step 2: Classify the image
    classification_result = classifier.predict(image_path)
    
    if classification_result:
        print(f"Image: {classification_result['filename']}")
        print(f"Predicted Class: {classification_result['predicted_label']} (Confidence: {classification_result['confidence']:.2f})")
        print(f"Processing Time: {classification_result['processing_time']:.4f} seconds")
        return classification_result
    else:
        print("Image classification failed.")
        return None

# Main function to run the pipeline
if __name__ == "__main__":
    # Define paths for the models and images
    model_path = r'C:\CitiDev\text_ocr\image_quality\inception_v3_model_newtrain_japan.h5'
    class_indices = {0: 'Driving_License', 1: 'Others', 2: 'Passport', 3: 'Residence_Card'}
    image_path = r'C:\CitiDev\text_ocr\image_quality\test_data\your_image.jpg'  # Modify this path
    
    # Initialize the ImageQualityAssessor and ImageClassifier
    image_quality_assessor = ImageQualityAssessor(blur_threshold=100.0)
    classifier = ImageClassifier(model_path, class_indices)

    # Process the image through the pipeline
    result = process_image(image_path, image_quality_assessor, classifier)
    
    if result:
        # Optionally save the result in a file or database, if needed
        pass
