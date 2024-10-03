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
from skimage.metrics import structural_similarity as ssim

def compare_images(image1_path, image2_path):
    # Load both images in grayscale
    image1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    # Check if images are loaded correctly
    if image1 is None or image2 is None:
        print("Image not found!")
        return False

    # Resize images to the same dimensions if needed (assume image1 is the template)
    image2_resized = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

    # Compute the Structural Similarity Index (SSIM)
    similarity_score, _ = ssim(image1, image2_resized, full=True)

    return similarity_score

# Paths to your correct image and the one to check
correct_image_path = 'path_to_correct_image'
check_image_path = 'path_to_check_image'

# Compare the two images
similarity_score = compare_images(correct_image_path, check_image_path)

# Define a threshold for similarity (e.g., 0.8 for 80% similarity)
threshold = 0.8

# Output the results
if similarity_score >= threshold:
    print(f"The images match with a similarity score of {similarity_score:.2f}.")
else:
    print(f"The images do not match. Similarity score: {similarity_score:.2f}.")
