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

import os
import numpy as np
import cv2  # Import OpenCV
import pandas as pd  # Import pandas for Excel output
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Step 1: Load the Best Model
model = load_model('best_inception_v3_model.h5')

# Step 2: Prepare Test Data
test_dir = 'path/to/test_images/'  # Path to the folder containing test images

# Step 3: Get Class Labels
class_indices = {0: 'cheques', 1: 'deposit', 2: 'driving license', 3: 'fund transfer', 4: 'passport', 5: 'residence certificate'}
class_labels = list(class_indices.values())

# Step 4: Load and Preprocess Images for Prediction
def load_and_preprocess_images(test_dir):
    images = []
    filenames = []
    
    # Loop through all files in the test directory
    for filename in os.listdir(test_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):  # Ensure the file is an image
            img_path = os.path.join(test_dir, filename)
            img = cv2.imread(img_path)  # Load the image using OpenCV
            if img is None:
                print(f"Failed to load image: {filename}")
                continue  # Skip this image if it can't be loaded
            img = cv2.resize(img, (299, 299))  # Resize to target size
            img_array = img.astype('float32') / 255.0  # Normalize pixel values
            images.append(img_array)  # Append to list
            filenames.append(filename)  # Keep track of the filename
    
    return np.array(images), filenames  # Convert to numpy array

# Load and preprocess the images
test_images, test_filenames = load_and_preprocess_images(test_dir)

# Step 5: Set a Confidence Threshold
confidence_threshold = 0.5  # Adjust the threshold as necessary

# Step 6: Make Predictions
predictions = model.predict(test_images)

# Prepare a list to store the results (filename and predicted class)
results = []

# Step 7: Print and Save Results
print("Predictions:")
for i, (filename, prediction) in enumerate(zip(test_filenames, predictions)):
    predicted_prob = np.max(prediction)  # Get the highest predicted probability
    predicted_class = np.argmax(prediction)  # Get the index of the highest probability

    if predicted_prob < confidence_threshold:
        predicted_label = 'Class not available'
    else:
        predicted_label = class_labels[predicted_class]
    
    print(f'{filename}: Predicted Class: {predicted_label} (Confidence: {predicted_prob:.2f})')
    # Append the result to the list for Excel export
    results.append([filename, predicted_label, predicted_prob])

    # Optionally, display the image with the prediction
    img_path = os.path.join(test_dir, filename)
    img = cv2.imread(img_path)  # Load the original image for display
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB format
        plt.imshow(img)  # Display the image
        plt.title(f'Predicted: {predicted_label} (Confidence: {predicted_prob:.2f})')
        plt.axis('off')  # Hide axes
        plt.show()

# Step 8: Save Results to Excel
df_results = pd.DataFrame(results, columns=['Image Name', 'Predicted Class', 'Confidence'])
excel_output_path = 'predictions_with_confidence.xlsx'
df_results.to_excel(excel_output_path, index=False)
print(f"Predictions saved to {excel_output_path}")
