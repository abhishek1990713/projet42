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
import os

# Parameters for testing
TEST_DATA_DIR = 'test_data/'  # Path to test dataset
BATCH_SIZE = 32

# Load the best saved model
loaded_model = load_model('Custom_CNN_best_model.h5')
print("Best model loaded successfully.")

# Prepare the test data generator
test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_directory(
    TEST_DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False  # Do not shuffle to maintain correct label order
)

# Evaluate the model on the test set
test_loss, test_accuracy = loaded_model.evaluate(test_generator)
print(f'Test Loss: {test_loss}, Test Accuracy: {test_accuracy}')

# Make predictions
test_generator.reset()
predictions = loaded_model.predict(test_generator)
predicted_classes = np.argmax(predictions, axis=1)
true_classes = test_generator.classes
class_labels = list(test_generator.class_indices.keys())

# Print predictions and true labels for each image
for i, (predicted_class, true_class) in enumerate(zip(predicted_classes, true_classes)):
    predicted_label = class_labels[predicted_class]
    true_label = class_labels[true_class]
    print(f"Image {i + 1}: Predicted - {predicted_label}, True - {true_label}")

# Classification report for the test set
test_report = classification_report(true_classes, predicted_classes, target_names=test_generator.class_indices.keys())
print(test_report)
