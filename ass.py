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
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# Function to load and preprocess the image
def load_and_preprocess_image(img_path, target_size=(256, 256)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img) / 255.0  # Normalize the image
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Function to make predictions on a single image
def predict_image(model, img_path, class_indices):
    img_array = load_and_preprocess_image(img_path)
    predictions = model.predict(img_array)
    predicted_class_idx = np.argmax(predictions, axis=1)[0]
    
    # Reverse the class_indices dictionary to map index to class name
    class_labels = {v: k for k, v in class_indices.items()}
    
    predicted_class = class_labels[predicted_class_idx]
    return predicted_class, predictions[0]

# Load the best saved model
model_path = 'Custom_CNN_best_model.h5'
best_model = load_model(model_path)
print(f"Model loaded from {model_path}")

# Load class indices
class_indices = train_generator.class_indices  # Should be the same as used during training

# Directory where your test images are stored
test_images_dir = 'test_images/'  # Replace with the path to your test images directory

# Loop through test images and make predictions
for img_file in os.listdir(test_images_dir):
    img_path = os.path.join(test_images_dir, img_file)
    predicted_class, confidence_scores = predict_image(best_model, img_path, class_indices)
    
    print(f"Image: {img_file}")
    print(f"Predicted Class: {predicted_class}")
    print(f"Confidence Scores: {confidence_scores}")
    print('---')
