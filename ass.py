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

import cv2

def preprocess_image(image_path):
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Resize the image to a fixed size (if needed, based on template dimensions)
    image_resized = cv2.resize(image, (640, 400))  # Resize to template size (example size)
    
    # Apply Gaussian Blur to reduce noise (optional)
    image_preprocessed = cv2.GaussianBlur(image_resized, (5, 5), 0)

    return image_preprocessed

def match_license_layout(template_path, check_image_path, threshold=0.75):
    # Preprocess both images
    template = preprocess_image(template_path)
    check_image = preprocess_image(check_image_path)

    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Detect keypoints and descriptors
    keypoints1, descriptors1 = orb.detectAndCompute(template, None)
    keypoints2, descriptors2 = orb.detectAndCompute(check_image, None)

    # Use BFMatcher to find the best matches
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort matches based on distance (lower is better)
    matches = sorted(matches, key=lambda x: x.distance)

    # Calculate good matches
    good_matches = [m for m in matches if m.distance < 50]

    # Match ratio
    match_ratio = len(good_matches) / len(matches)

    return match_ratio >= threshold

# Paths to your template and image to check
template_image_path = 'path_to_template_license'
check_image_path = 'path_to_check_image'

# Compare layout
is_matching = match_license_layout(template_image_path, check_image_path)

if is_matching:
    print("The layout of the check image matches the template.")
else:
    print("The layout of the check image does NOT match the template.")
