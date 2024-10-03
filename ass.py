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

from paddleocr import PaddleOCR
import cv2

# Initialize the PaddleOCR model (Japanese language model)
ocr = PaddleOCR(use_angle_cls=True, lang='japan')

def extract_text_and_boxes(image_path):
    # Use OCR to extract text and bounding boxes
    result = ocr.ocr(image_path, cls=True)

    # Collect bounding boxes and text
    boxes = []
    for page in result:
        for line in page:
            # Extract box coordinates
            box = line[0]
            text = line[1][0]
            boxes.append((box, text))
    
    return boxes

def compare_text_layout(template_boxes, check_boxes, threshold=0.7):
    matched_boxes = 0

    # Compare the number of boxes and their positions (You can also compare the text if needed)
    if len(template_boxes) != len(check_boxes):
        print("Different number of text blocks detected.")
        return False

    for i in range(len(template_boxes)):
        # Compare the positions of the bounding boxes
        template_box = template_boxes[i][0]
        check_box = check_boxes[i][0]

        # Calculate overlap or distance between bounding boxes (using IoU or other methods)
        distance = sum([abs(template_box[j] - check_box[j]) for j in range(len(template_box))]) / len(template_box)

        # If the distance is within a threshold, consider it a match
        if distance < threshold:
            matched_boxes += 1

    # If the majority of the boxes match, the layout is considered the same
    match_ratio = matched_boxes / len(template_boxes)
    
    return match_ratio >= threshold

# Paths to the correct license (template) and the one to check
template_image_path = 'path_to_template_license'
check_image_path = 'path_to_check_image'

# Extract text layout (boxes) from both images
template_boxes = extract_text_and_boxes(template_image_path)
check_boxes = extract_text_and_boxes(check_image_path)

# Compare the layouts
is_matching = compare_text_layout(template_boxes, check_boxes)

# Output the result
if is_matching:
    print("The layout of the check image matches the template.")
else:
    print("The layout of the check image does NOT match the template.")
