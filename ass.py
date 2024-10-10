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
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

# Step 1: Load the Best Model
model = load_model('best_inception_v3_model.h5')

# Step 2: Prepare Test Data
test_dir = 'path/to/test_images/'  # Ensure this folder contains subfolders for classes

# Create an ImageDataGenerator for the test images
test_datagen = ImageDataGenerator(rescale=1.0/255)  # Normalize pixel values

# Load test data from the folder
test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(299, 299),  # InceptionV3 requires 299x299 images
    batch_size=1,
    class_mode=None,  # No labels needed
    shuffle=False  # Keep the order of the images
)

# Check the number of test samples
print(f"Number of test samples: {test_generator.samples}")

# Step 3: Make Predictions
if test_generator.samples > 0:  # Ensure there are samples to predict
    predictions = model.predict(test_generator)

    # Step 4: Get Predicted Classes
    predicted_classes = np.argmax(predictions, axis=1)

    # Print predicted classes
    print("Predicted Classes:")
    print(predicted_classes)

    # Step 5: Display Results
    class_indices = test_generator.class_indices
    class_labels = list(class_indices.keys())
    print("Class Labels:", class_labels)

    # Display each image with its predicted class
    for i in range(len(predicted_classes)):
        img = test_generator[i][0]  # Get the image
        plt.imshow(img)  # Display the image
        plt.title(f'Predicted: {class_labels[predicted_classes[i]]}')
        plt.axis('off')  # Hide axes
        plt.show()
else:
    print("No test samples found.")
