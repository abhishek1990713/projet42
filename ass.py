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

def match_license_layout(template_path, check_image_path, threshold=0.75):
    # Load both images in grayscale
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    check_image = cv2.imread(check_image_path, cv2.IMREAD_GRAYSCALE)

    # Check if images are loaded correctly
    if template is None or check_image is None:
        print("Template or check image not found!")
        return False

    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Detect keypoints and descriptors for both images
    keypoints1, descriptors1 = orb.detectAndCompute(template, None)
    keypoints2, descriptors2 = orb.detectAndCompute(check_image, None)

    # Use BFMatcher to find the best matches
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort matches based on distance (the lower, the better)
    matches = sorted(matches, key=lambda x: x.distance)

    # Calculate the number of good matches
    good_matches = [m for m in matches if m.distance < 50]

    # Calculate the match ratio
    match_ratio = len(good_matches) / len(matches)

    # If match ratio exceeds the threshold, the layouts are considered matching
    return match_ratio >= threshold

# Paths to your template (correct image) and the image to check
template_image_path = 'path_to_template_license'
check_image_path = 'path_to_check_image'

# Match the layout of the check image to the template
is_matching = match_license_layout(template_image_path, check_image_path)

# Output the result
if is_matching:
    print("The layout of the check image matches the template.")
else:
    print("The layout of the check image does NOT match the template.")
