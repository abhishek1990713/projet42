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

# Initialize the PaddleOCR model for Japanese language
ocr = PaddleOCR(use_angle_cls=True, lang='japan')

# Define the specific Japanese keywords for driving license and passport
driving_license_keywords = ["氏名", "日生", "本籍", "住所", "支払", "免許の", "条件等", "号", "公安委員会"]
passport_keywords = ["氏名", "生年月日", "国籍", "旅券番号", "発行日", "有効期限", "発行機関"]

def identify_image_type(image_path):
    """Identify if the image is a Driving License or Passport."""
    # This is a simple implementation. You can enhance it using image features or filename patterns.
    if "driving" in image_path.lower() or "license" in image_path.lower():
        return "driving_license"
    elif "passport" in image_path.lower():
        return "passport"
    else:
        return "unknown"

def check_keywords_in_image(image_path):
    """Extract text from image and check for the presence of specific keywords."""
    result = ocr.ocr(image_path, cls=True)

    # Gather all extracted text into a single string
    extracted_text = ""
    for page in result:
        for line in page:
            extracted_text += line[1][0] + " "
    
    # Identify the image type
    image_type = identify_image_type(image_path)
    
    # Check for the presence of each keyword based on image type
    if image_type == "driving_license":
        keywords = driving_license_keywords
    elif image_type == "passport":
        keywords = passport_keywords
    else:
        return "Unknown image type."

    # Check for missing keywords
    missing_keywords = [keyword for keyword in keywords if keyword not in extracted_text]

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
            result = check_keywords_in_image(image_path)
            print(f"{filename}: {result}")

# Folder containing the images
folder_path = 'path_to_image_folder'  # Replace with your folder path

# Check all images in the folder and print results
check_images_in_folder(folder_path)
