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
from paddleocr import PaddleOCR
from PIL import Image, ImageEnhance

# Initialize the PaddleOCR model for Japanese language
ocr = PaddleOCR(use_angle_cls=True, lang='japan')

# Define the specific Japanese keywords to check
field_keywords = ["氏名", "日生", "本籍", "住所", "支払", "免許の", "条件等", "号", "公安委員会"]

def preprocess_image(image_path):
    """Resize the image to 600x600, set DPI to 500, and darken the image."""
    img = Image.open(image_path)
    
    # Resize the image to 600x600
    img = img.resize((600, 600))
    
    # Set the DPI to 500 (Pillow sets DPI via the 'info' dictionary when saving)
    img.info['dpi'] = (500, 500)
    
    # Darken the image by enhancing the contrast (use ImageEnhance module)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Adjust this factor to make the text darker

    # Save the preprocessed image in a temporary file (overwrite the original image)
    preprocessed_image_path = image_path.replace(".png", "_preprocessed.png").replace(".jpg", "_preprocessed.jpg").replace(".jpeg", "_preprocessed.jpeg")
    img.save(preprocessed_image_path, dpi=(500, 500))
    
    return preprocessed_image_path

def check_keywords_in_image(image_path, field_keywords):
    """Extract text from image and check for the presence of specific keywords."""
    # Preprocess the image first (resize, set DPI, darken text)
    preprocessed_image_path = preprocess_image(image_path)

    # Run OCR on the preprocessed image
    result = ocr.ocr(preprocessed_image_path, cls=True)
    
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

def check_images_in_folder(folder_path, field_keywords):
    """Check all images in the folder and print whether each is Good or Not Good."""
    for filename in os.listdir(folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):  # Process only image files
            image_path = os.path.join(folder_path, filename)
            result = check_keywords_in_image(image_path, field_keywords)
            print(f"{filename}: {result}")

# Folder containing the images
folder_path = 'path_to_image_folder'  # Replace with your folder path

# Check all images in the folder and print results
check_images_in_folder(folder_path, field_keywords)

