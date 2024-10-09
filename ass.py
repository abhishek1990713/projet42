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
import numpy as np
import pandas as pd
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.vgg16 import preprocess_input

# Parameters
IMG_SIZE = 256  # The image size used in training
MODEL_PATH = 'Custom_CNN_best_model.h5'  # Path to the best saved model
TEST_FOLDER = 'path_to_test_folder/'  # Folder containing test images
RESULTS_CSV = 'test_results.csv'  # CSV file to save results
CLASS_LABELS = {0: 'Passport', 1: 'Driving License', 2: 'Healthcare'}  # Class labels mapping

# Load the saved model
model = load_model(MODEL_PATH)

# Function to predict class of a single image
def predict_image(img_path, model):
    # Load image using tensorflow.keras.utils.load_img
    img = load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    
    # Convert image to array
    img_array = img_to_array(img)
    
    # Expand dimensions to match the input shape of the model (1, IMG_SIZE, IMG_SIZE, 3)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Preprocess the image for the model (same preprocessing used during training)
    img_array = preprocess_input(img_array)
    
    # Make prediction
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)[0]  # Get the index of the highest probability
    predicted_label = CLASS_LABELS[predicted_class]
    confidence = predictions[0][predicted_class]
    
    return predicted_label, confidence

# Function to test all images in a folder
def test_images_in_folder(folder_path, model):
    results = []
    
    # Loop through all files in the folder
    for img_file in os.listdir(folder_path):
        # Ensure it's an image file
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(folder_path, img_file)
            
            # Predict the class of the image
            predicted_label, confidence = predict_image(img_path, model)
            
            # Append results (image name, predicted class, confidence)
            results.append({
                'Image': img_file,
                'Predicted Class': predicted_label,
                'Confidence': confidence
            })
    
    return results

# Run the test
test_results = test_images_in_folder(TEST_FOLDER, model)

# Convert results to DataFrame
df_results = pd.DataFrame(test_results)

# Save results to CSV
df_results.to_csv(RESULTS_CSV, index=False)

print(f'Results saved to {RESULTS_CSV}')
