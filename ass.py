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
import os
import cv2
import numpy as np

def preprocess_image(image_path):
    """Preprocess the image to enhance text for better OCR results."""
    # Read the image
    image = cv2.imread(image_path)

    # Check if the image was loaded correctly
    if image is None:
        print(f"Error loading image: {image_path}")
        return None

    # Resize the image to increase size (for example, scale by a factor of 2)
    height, width = image.shape[:2]
    new_size = (int(width * 2), int(height * 2))
    resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)

    # Convert to grayscale
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Apply a fixed binary threshold to convert to black and white
    _, binary_image = cv2.threshold(blurred_image, 150, 255, cv2.THRESH_BINARY)

    # Save the processed image temporarily
    processed_image_path = "processed_" + os.path.basename(image_path)
    cv2.imwrite(processed_image_path, binary_image)

    return processed_image_path

def preprocess_images_in_folder(folder_path):
    """Preprocess all images in the folder and save them."""
    processed_images = []
    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):  # Process only image files
            image_path = os.path.join(folder_path, filename)
            processed_image_path = preprocess_image(image_path)
            if processed_image_path:
                processed_images.append(processed_image_path)
                print(f"Processed: {filename} -> {processed_image_path}")

    return processed_images

# Folder containing the images
folder_path = 'path_to_image_folder'  # Replace with your folder path

# Process all images in the folder
processed_images = preprocess_images_in_folder(folder_path)

# Now you can run OCR on processed images if needed
