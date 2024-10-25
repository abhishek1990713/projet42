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


@app.route('/predict', methods=['POST'])
def Upload():
    if request.method == 'POST':
        # print(request.json['file'])

        def download_all_objects_in_folder(xyz):
            print(xyz)
            print("location ")
            print(request.json['file'])
            _BUCKET_NAME = 'sbr-project-2021'
            _PREFIX = xyz

            session = boto3.Session(
                aws_access_key_id='AKIAQRGY6UM3ZUL5MUCG',
                aws_secret_access_key='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'
            )
            resource = session.resource('s3').Bucket(_BUCKET_NAME).download_file(xyz,
                                                                                 'inp/splite.wav')
            # s3_resource = session.resource('s3')
            # my_bucket = s3_resource.Bucket(_BUCKET_NAME)
            # resource = s3_resource.download_file(_BUCKET_NAME, request.json['file'],  'video_name/xyz.mp4')

            return None

        print(request.json['user_id'])

        download_all_objects_in_folder(
            'machine learning/' + request.json['user_id'] + '/output/' + request.json['post_id'] + 'audo12.wav')

        r = sr.Recognizer()

        sound = AudioSegment.from_wav("inp/splite.wav")

        audio_chunks = split_on_silence(sound, min_silence_len=2000, silence_thresh=sound.dBFS - 14, keep_silence=500)
        whole_text = ""
        textMap = {}
        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join('InputFiles', f"speech_chunk{i}.wav")
            print("Exporting file", output_file)
            result = chunk.export(output_file, format="wav")

        _BUCKET_NAME = 'sbr-project-2021'

        session = boto3.Session(
            aws_access_key_id='AKIAQRGY6UM3ZUL5MUCG',
            aws_secret_access_key='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'
        )
        s3 = session.resource('s3')
        files = glob.glob('InputFiles' + "/*")
        print(files)
        length = len(files)
        print(length)
        array = []
        for i in range(length):
            s3.Bucket(_BUCKET_NAME).upload_file(files[i],
                                                "machine learning/" + request.json[
                                                    'user_id'] + "/splited_audio/" + 'chunks' + str(i) + '.wav')

        data = {'name': "machine learning/" + request.json['user_id'] + "/splited_audio/"}

        os.remove("inp/splite.wav")
        return jsonify(data)

    # return str(result)
    return None


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=6000, debug=True)

from fastapi import FastAPI, File, Form, UploadFile
from pathlib import Path
from typing import Annotated
from PIL import Image
import io
import asyncio
import base64
import os
import ssl
import sys
import logging
from utility import doc_to_ocr
from constant import *
from configobj import ConfigObj
from cryptography.fernet import Fernet
from setup_log import setup_logger
from datetime import datetime

# Initialize the FastAPI app
app = FastAPI()

# Load configuration
config = ConfigObj("CONFIG_FILE_PATH")  # Replace with your actual config file path
language = config['PARAMETER']['LANGUAGE_CODE']
timeout = int(config['PARAMETER']['TIMEOUT'])
end_point = config['PARAMETER']['ENDPOINT']
enc_key_config = config['CERT_STRING']['ENC_KEY']
enc_cert_pass_config = config['CERT_STRING']['ENC_CERT_PASS'].encode('utf-8')

# Setup SSL context
ssl_cert_path = "CERT_PATH"  # Replace with actual path
ssl_key_path_encrypted = "PRIVATE_KEY_PATH"  # Replace with actual path
with open(ssl_cert_path, 'rb') as cert_file:
    certificate = cert_file.read()
with open(ssl_key_path_encrypted, 'rb') as key_file:
    encrypted_key = key_file.read()

cipher_suite = Fernet(enc_key_config)
decrypted_password = cipher_suite.decrypt(enc_cert_pass_config).decode('utf-8')

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=ssl_cert_path, keyfile=ssl_key_path_encrypted, password=decrypted_password)
context.verify_mode = ssl.CERT_REQUIRED

# Set up logging
try:
    logger = setup_logger()
except Exception as e:
    print("LOG SETUP ERROR:", e)

@app.post("/endpoint")  # Replace "/endpoint" with your actual endpoint path
async def get_file_and_data(
    file: UploadFile = File(...),
    refNo: str = Form(...),
    lang: str = Form('')
):
    """
    API method to read file, reference number, and language parameter from the request form.
    file --> actual image file for OCR
    refNo --> unique number for given file
    lang --> language parameter for OCR, default is taken from config file if not provided
    """
    logger.info("API CALLED")
    
    # Print request details
    try:
        print(file.filename, refNo, lang)
        logger.info(f"Processing file: {file.filename}, refNo: {refNo}")
    except Exception as e:
        logger.info("LOG REF ERROR")
        return {"ERROR_KEY": "LOG_REF_ERROR"}
    
    # Check if refNo is valid
    if refNo in (None, '', 'EDGSTR'):
        return {"ERROR_KEY": "LOG_REF_ERROR"}

    # Prepare file path
    current_directory = os.getcwd()
    input_path = os.path.join(current_directory, "INPUT_PATH")  # Replace with actual input path
    os.makedirs(input_path, exist_ok=True)
    new_path = os.path.join(input_path, file.filename)
    
    # Save the uploaded file
    with open(new_path, 'wb') as file_object:
        file_object.write(await file.read())

    # Determine the language for OCR
    if not lang:
        lang = language
    
    try:
        # Call OCR processing function
        ocr_result, page_no = doc_to_ocr(new_path, lang, refNo, timeout)
        
        # Remove the file after processing
        os.remove(new_path)
        
        return {
            "OCRRESULT": ocr_result,
            "NOOFPAGES": page_no,
            "REFNO": refNo
        }
    except OSError as error:
        logger.exception(f"Input error: {error}")
        return {"ERROR_KEY": "INPUT_ERROR"}
    except Exception as e:
        logger.exception(f"Error in API function: {e}")
        return {"ERROR_KEY": "PARAMETER_ERROR", "REMARK": str(e)}
