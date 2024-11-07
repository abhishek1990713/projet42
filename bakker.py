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

class ImageClassifier:
    def __init__(self, model_path, class_indices, image_size=(299, 299), confidence_threshold=0.35):
        # Load the pre-trained model
        self.model = load_model(model_path)
        # Store class indices and labels
        self.class_indices = class_indices
        self.class_labels = list(class_indices.values())
        # Image size and confidence threshold
        self.image_size = image_size
        self.confidence_threshold = confidence_threshold

    def load_and_preprocess_image(self, image_path):
        """Load and preprocess a single image."""
        img = cv2.imread(image_path)
        if img is None:
            print(f"Failed to load image: {image_path}")
            return None

        # Resize image to model input size
        img = cv2.resize(img, self.image_size)
        img_array = img.astype('float32') / 255.0  # Normalize image
        return np.expand_dims(img_array, axis=0)  # Add batch dimension

    def predict(self, image_path):
        """Predict the class of a single image."""
        # Load and preprocess the image
        test_image = self.load_and_preprocess_image(image_path)
        if test_image is None:
            return None

        # Measure time taken for prediction
        start_time = time.time()

        # Make prediction
        prediction = self.model.predict(test_image)

        end_time = time.time()
        processing_time = end_time - start_time

        # Extract prediction details
        predicted_prob = np.max(prediction)
        predicted_class = np.argmax(prediction)

        # Assign label based on confidence
        if predicted_prob < self.confidence_threshold:
            predicted_label = 'Others'
        else:
            predicted_label = self.class_labels[predicted_class]

        return {
            'filename': image_path,
            'predicted_label': predicted_label,
            'confidence': predicted_prob,
            'processing_time': processing_time
        }

# Usage
if __name__ == "__main__":
    # Define the model path and class indices
    model_path = r'C:\CitiDev\text_ocr\image_quality\inception_v3_model_newtrain_japan.h5'
    class_indices = {0: 'Driving_License', 1: 'Others', 2: 'Passport', 3: 'Residence_Card'}
    
    # Create an instance of the ImageClassifier
    classifier = ImageClassifier(model_path, class_indices)

    # Path to the image to be processed
    image_path = r'C:\CitiDev\text_ocr\image_quality\test_data\your_image.jpg'  # Modify this path

    # Get predictions for the image
    result = classifier.predict(image_path)

    if result:
        # Print the result
        print(f"Image: {result['filename']}")
        print(f"Predicted Class: {result['predicted_label']} (Confidence: {result['confidence']:.2f})")
        print(f"Processing Time: {result['processing_time']:.4f} seconds")

