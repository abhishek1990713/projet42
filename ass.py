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
import numpy as np

# Initialize the PaddleOCR model for Japanese language
ocr = PaddleOCR(use_angle_cls=True, lang='japan')

# Define the specific Japanese keywords to extract
field_keywords = ["氏名", "日生", "本籍", "住所", "支払", "免許の", "条件等", "号", "公安委員会"]

def extract_fields(image_path, field_keywords):
    """Extract the bounding boxes of specific fields from the image using OCR."""
    result = ocr.ocr(image_path, cls=True)
    
    # Dictionary to store detected fields
    fields = {keyword: [] for keyword in field_keywords}
    
    for page in result:
        for line in page:
            text = line[1][0]
            box = line[0]
            
            # Check if the text contains any of the defined keywords
            for keyword in field_keywords:
                if keyword in text:
                    fields[keyword].append(box)
    
    return fields

def compare_field_layout(template_fields, check_fields, threshold=0.1):
    """Compare the layout of extracted field bounding boxes from both images."""
    
    # Compare the number of bounding boxes for each field
    for keyword in field_keywords:
        if len(template_fields[keyword]) != len(check_fields[keyword]):
            return False

    # Compare bounding boxes for each keyword field
    def compare_boxes(boxes1, boxes2):
        """Compare the positions and sizes of bounding boxes."""
        for b1, b2 in zip(boxes1, boxes2):
            # Convert lists of corner points to NumPy arrays for cv2.boundingRect
            np_b1 = np.array(b1, dtype=np.int32)
            np_b2 = np.array(b2, dtype=np.int32)
            
            # Use boundingRect to get x, y, width, height for both boxes
            x1, y1, w1, h1 = cv2.boundingRect(np_b1)
            x2, y2, w2, h2 = cv2.boundingRect(np_b2)
            
            # Calculate if the bounding boxes are similar (within the threshold)
            if abs(w1 - w2) > threshold * w1 or abs(h1 - h2) > threshold * h1:
                return False
        return True
    
    # Compare bounding boxes for each field
    for keyword in field_keywords:
        if not compare_boxes(template_fields[keyword], check_fields[keyword]):
            return False

    return True

# Paths to the template and the check image
template_image_path = 'path_to_template_license'
check_image_path = 'path_to_check_image'

# Extract field layouts from both images
template_fields = extract_fields(template_image_path, field_keywords)
check_fields = extract_fields(check_image_path, field_keywords)

# Compare the layouts
is_matching = compare_field_layout(template_fields, check_fields)

# Output the result
if is_matching:
    print("The layout of the check image matches the template.")
else:
    print("The layout of the check image does NOT match the template.")
