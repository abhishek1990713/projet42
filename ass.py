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

def preprocess_image_for_contours(image_path):
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Resize the image to a standard size (adjust according to template size)
    image_resized = cv2.resize(image, (640, 400))  # Example size

    # Apply Gaussian Blur to reduce noise
    image_blur = cv2.GaussianBlur(image_resized, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(image_blur, 50, 150)

    return edges

def get_contours(image):
    # Find contours from the edges
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def match_license_contours(template_path, check_image_path, similarity_threshold=0.15):
    # Preprocess both images for contour detection
    template_edges = preprocess_image_for_contours(template_path)
    check_image_edges = preprocess_image_for_contours(check_image_path)

    # Get contours for both images
    template_contours = get_contours(template_edges)
    check_image_contours = get_contours(check_image_edges)

    # If no contours found, return False
    if len(template_contours) == 0 or len(check_image_contours) == 0:
        print("No contours found in one or both images!")
        return False

    # Compare the largest contour of both images (assuming the license borders are the largest contour)
    template_contour = max(template_contours, key=cv2.contourArea)
    check_image_contour = max(check_image_contours, key=cv2.contourArea)

    # Match the shapes using Hu Moments (cv2.matchShapes)
    similarity_score = cv2.matchShapes(template_contour, check_image_contour, cv2.CONTOURS_MATCH_I1, 0.0)

    # Return True if the similarity score is below the threshold
    return similarity_score < similarity_threshold

# Paths to the correct license (template) and the one to check
template_image_path = 'path_to_template_license'
check_image_path = 'path_to_check_image'

# Match contours
is_matching = match_license_contours(template_image_path, check_image_path)

# Output the result
if is_matching:
    print("The layout of the check image matches the template.")
else:
    print("The layout of the check image does NOT match the template.")
