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
    """Preprocess the image to enhance text for better OCR results and save it in the output folder."""
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

    # Construct the output path
    processed_image_path = os.path.join(output_folder, "processed_" + os.path.basename(image_path))
    
    # Save the processed image in the output folder
    cv2.imwrite(processed_image_path, binary_image)

    return processed_image_path

def preprocess_images_in_folder(input_folder, output_folder):
    """Preprocess all images in the input folder and save them in the output folder."""
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    processed_images = []
    for filename in os.listdir(input_folder):
        if filename.endswith((".png", ".jpg", ".jpeg")):  # Process only image files
            image_path = os.path.join(input_folder, filename)
            processed_image_path = preprocess_image(image_path, output_folder)
            if processed_image_path:
                processed_images.append(processed_image_path)
                print(f"Processed: {filename} -> {processed_image_path}")

    return processed_images

# Folders for input and output
input_folder = 'path_to_input_folder'  # Replace with your input folder path
output_folder = 'path_to_output_folder'  # Replace with your output folder path

# Process all images in the input folder and save to the output folder
processed_images = preprocess_images_in_folder(input_folder, output_folder)
