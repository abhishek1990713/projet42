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


import cv2
import numpy as np
import warnings

# Suppress warnings
warnings.simplefilter('ignore')

class ImageQualityAssessor:
    def __init__(self, blur_threshold=100.0):
        """
        Initialize the ImageQualityAssessor class with a blur threshold.
        :param blur_threshold: The threshold for the Laplacian variance to classify an image as blurry.
        """
        self.blur_threshold = blur_threshold

    def is_image_blurry(self, image_path):
        """
        Determines whether the image is blurry or sharp using the Laplacian variance method.
        :param image_path: Path to the image.
        :return: "Blurry" if the image is considered blurry, "Sharp" otherwise.
        """
        # Read the image
        img = cv2.imread(image_path)
        
        if img is None:
            print("Error: Could not load image.")
            return None

        # Convert the image to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Compute the Laplacian of the image and then the variance
        laplacian = cv2.Laplacian(gray_img, cv2.CV_64F)
        variance = laplacian.var()

        print(f"Laplacian Variance: {variance}")

        # If variance is below the threshold, the image is considered blurry
        return "Blurry" if variance < self.blur_threshold else "Sharp"

# Usage Example:

# Initialize the ImageQualityAssessor with the desired blur threshold
image_quality_assessor = ImageQualityAssessor(blur_threshold=100.0)

# Path to the image
image_path = r"C:\CitiDev\text_ocr\image_quality\augmented_me_images.png"

# Get result
result = image_quality_assessor.is_image_blurry(image_path)
print(f"The image is: {result}")

