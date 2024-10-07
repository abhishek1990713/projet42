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
from paddleocr import PaddleOCR

# Initialize the PaddleOCR model for Japanese language
ocr = PaddleOCR(use_angle_cls=True, lang='japan')

# Define the specific Japanese keywords for driving license and passport
driving_license_keywords = ["氏名", "日生", "本籍", "住所", "支払", "免許の", "条件等", "号", "公安委員会"]
passport_keywords = ["氏名", "国籍", "生年月日", "パスポート番号", "有効期限", "発行日", "発行機関"]

def preprocess_image(image_path):
    """Preprocess the image by darkening the text."""
    # Read the image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to darken the text
    _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)

    # Save the processed image temporarily
    processed_image_path = "processed_" + os.path.basename(image_path)
    cv2.imwrite(processed_image_path, thresh_image)

    return processed_image_path

def identify_document_type(image_path):
    """Identify if the document is a driving license or passport based on keywords."""
    # Preprocess the image
    processed_image_path = preprocess_image(image_path)

    # Perform OCR on the processed image
    result = ocr.ocr(processed_image_path, cls=True)
    
    # Gather all extracted text into a single string
    extracted_text = ""
    for page in result:
        for line in page:
            extracted_text += line[1][0] + " "
    
    # Check for keywords related to driving license and passport
    is_driving_license = any(keyword in extracted_text for keyword in driving_license_keywords)
    is_passport = any(keyword in extracted_text for keyword in passport_keywords)
    
    if is_driving_license:
        return "Driving License"
    elif is_passport:
        return "Passport"
    else:
        return "Unknown Document"

def check_keywords_in_image(image_path, document_type):
    """Extract text from image and check for the presence of specific keywords."""
    if document_type == "Driving License":
        field_keywords = driving_license_keywords
    elif document_type == "Passport":
        field_keywords = passport_keywords
    else:
        return "Document type unknown; cannot check keywords."

    # Preprocess the image
    processed_image_path = preprocess_image(image_path)

    # Perform OCR on the processed image
    result = ocr.ocr(processed_image_path, cls=True)
    
    # Gather all extracted text into a single string
    extracted_text = ""
    for page in result:
        for line in page:
            extracted_text += line[1][0] + " "
    
    # Check for the presence of each keyword
    missing_keywords = []
    for keyword in field_keywords:
        if keyword not in extracted_text:
            missing_keywords.append(keyword)
    
    # Return result
    if len(missing_keywords) == 0:
        return "Image is Good"  # All keywords are present
    else:
        return f"Image is not Good: Missing keywords: {', '.join(missing_keywords)}"

def check_images_in_folder(folder_path):
    """Check all images in the folder and print whether each is Good or Not Good."""
    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):  # Process only image files
            image_path = os.path.join(folder_path, filename)
            document_type = identify_document_type(image_path)
            result = check_keywords_in_image(image_path, document_type)
            print(f"{filename}: {result}")

# Folder containing the images
folder_path = 'path_to_image_folder'  # Replace with your folder path

# Check all images in the folder and print results
check_images_in_folder(folder_path)
