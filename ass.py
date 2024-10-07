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

def preprocess_image(image_path, output_folder):
    """Preprocess the image by resizing and enhancing the text."""
    # Read the image
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Unable to read the image {image_path}. Skipping.")
        return  # Return if the image could not be read

    # Resize the image (e.g., double the size)
    height, width = image.shape[:2]
    new_width = int(width * 2)  # Increase width by a factor (e.g., 2)
    new_height = int(height * 2)  # Increase height by a factor (e.g., 2)
    resized_image = cv2.resize(image, (new_width, new_height))

    # Convert to grayscale
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    # Apply histogram equalization to enhance contrast
    enhanced_image = cv2.equalizeHist(gray_image)

    # Apply a binary threshold to darken the text
    _, thresh_image = cv2.threshold(enhanced_image, 150, 255, cv2.THRESH_BINARY_INV)

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the processed image
    output_image_path = os.path.join(output_folder, os.path.basename(image_path))
    cv2.imwrite(output_image_path, thresh_image)

    print(f"Processed and saved: {output_image_path}")

def process_images_in_folder(input_folder, output_folder):
    """Process all images in the input folder and save them to the output folder."""
    for filename in os.listdir(input_folder):
        if filename.endswith((".png", ".jpg", ".jpeg")):  # Process only image files
            image_path = os.path.join(input_folder, filename)
            preprocess_image(image_path, output_folder)

# Specify the input and output folders
input_folder = 'path_to_input_folder'  # Replace with your input folder path
output_folder = 'path_to_output_folder'  # Replace with your desired output folder path

# Process all images in the input folder
process_images_in_folder(input_folder, output_folder)
