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

from ultralytics import YOLO

# Define model path and input file path
model_path = r"C:\CitiDev\text_ocr\yolo_model\yolov8m.pt"
input_file_path = r"C:\CitiDev\text_ocr\yolo_model\Passport\augmented_ad_6526ci@k.png"

# Load the model
model = YOLO(model_path)

# Run inference on the input file
results = model(input_file_path)

# Threshold for confidence score
confidence_threshold = 0.70

# Flags to check conditions
all_boxes_present = False
confidence_check = False

# Process results list
for result in results:
    boxes = result.boxes  # Bounding boxes
    if boxes is not None and len(boxes) == 4:
        all_boxes_present = True
    else:
        print("Not all four bounding boxes are present.")
    
    # Check confidence scores
    confidence_scores = boxes.conf if boxes is not None else []
    if all(score >= confidence_threshold for score in confidence_scores):
        confidence_check = True
    else:
        print("Some confidence scores are below the threshold of 0.70.")

    # Display keypoints, probabilities, and oriented bounding boxes
    keypoints = result.keypoints
    print("Keypoints:", keypoints)
    
    probs = result.probs
    print("Probability:", probs)

    obb = result.obb
    print("Oriented Boxes:", obb)

    # Show the result
    result.show()  # Display the image with results
    result.save(filename="test_result.jpg")  # Save to disk

# Final check based on conditions
if all_boxes_present and confidence_check:
    print("Image is good.")
else:
    print("Image is not good.")
