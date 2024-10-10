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
            img = cv2.resize(img, (299, 299))  # Resize to target size
            img_array = img.astype('float32') / 255.0  # Normalize pixel values
            images.append(img_array)  # Append to list
            filenames.append(filename)  # Keep track of the filename
    
    return np.array(images), filenames  # Convert to numpy array

# Load and preprocess the images
test_images, test_filenames = load_and_preprocess_images(test_dir)

# Step 5: Make Predictions
predictions = model.predict(test_images)

# Step 6: Get Predicted Classes
predicted_classes = np.argmax(predictions, axis=1)

# Print the predicted classes with filenames
print("Predictions:")
for filename, predicted_class in zip(test_filenames, predicted_classes):
    print(f'{filename}: Predicted Class: {class_labels[predicted_class]}')

# Step 7: Display Results
for i, filename in enumerate(test_filenames):
    img_path = os.path.join(test_dir, filename)
    img = cv2.imread(img_path)  # Load the original image for display
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB format
    plt.imshow(img)  # Display the image
    plt.title(f'Predicted: {class_labels[predicted_classes[i]]}')
    plt.axis('off')  # Hide axes
    plt.show()
