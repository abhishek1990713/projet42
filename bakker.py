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
from flask import Flask, request, jsonify
from pathlib import Path
from PIL import Image
import io
import asyncio
import base64
from utility import doc_to_ocr  # Import your OCR function
import os
import sys
from configobj import ConfigObj
from cryptography.fernet import Fernet
import logging
from datetime import datetime
import ssl  # For SSL context

# Setup the Flask app
app = Flask(__name__)

# Load constants and configuration
try:
    from constant import *  # Import any project constants
    config = ConfigObj('config.ini')  # Ensure config.ini is correctly set
except Exception as e:
    print(f"Configuration Error: {e}")
    sys.exit(1)  # Exit if the configuration can't be loaded

# Initialize logging
try:
    from setup_log import setup_logger
    logger = setup_logger()
except Exception as e:
    print(f"Log Setup Error: {e}")
    logger = None  # Log setup failed, set logger to None

# Load encryption key and certificate configurations
try:
    ssl_key_path_encrypted = config['CERT_STRING'].get('SSL_KEY_ENC', 'path/to/ssl_key_enc')
    ssl_cert_path = config['CERT_STRING'].get('SSL_CERT', 'path/to/cert')
    enc_key_config = config['CERT_STRING']['ENC_KEY']
    enc_cert_pass_config = config['CERT_STRING']['ENC_CERT_PASS'].encode("utf-8")

    # Decrypt the certificate password
    cipher_suite = Fernet(enc_key_config)
    decrypted_password = cipher_suite.decrypt(enc_cert_pass_config).decode("utf-8")
except KeyError as e:
    print(f"Missing configuration key: {e}")
    sys.exit(1)

@app.route('/tmp_python_ocr_ref', methods=['POST'])
def process_file_to_ocr():
    """Process uploaded file with OCR."""
    if not logger:
        return jsonify({"ERROR_KEY": "Logger not initialized"}), 500

    try:
        # Log API call
        logger.info("OCR API called")

        # Get file, language, and reference number from request
        file = request.files.get('file')
        refNo = request.form.get('refNo')
        lang = request.form.get('lang', config['PARAMETER'].get('LANGUAGE_CODE'))

        # Validate required fields
        if not file or not refNo:
            return jsonify({"ERROR_KEY": "109 REFERBOR"})

        # Define file storage path
        current_directory = os.getcwd()
        input_path = os.path.join(current_directory, "input_path")
        os.makedirs(input_path, exist_ok=True)

        # Save file for OCR processing
        file_path = os.path.join(input_path, file.filename)
        file.save(file_path)

        # Run OCR
        timeout = int(config['PARAMETER'].get('TIMEOUT', 30))
        ocr_result, pg_no = doc_to_ocr(file_path, lang, refNo, timeout)

        # Clean up saved file
        os.remove(file_path)

        # Return OCR results
        return jsonify({
            "OCRRESULT": ocr_result,
            "NOOFPAGES": pg_no,
            "REFNO": refNo
        })

    except OSError as error:
        logger.exception("File processing error")
        return jsonify({"ERROR_KEY": "INPUT_ERROR"}), 500
    except Exception as e:
        logger.exception("API function error")
        return jsonify({"REMARK": str(e), "ERROR_KEY": "PARAMETER_ERROR"}), 500

if __name__ == '__main__':
    # SSL context setup
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=ssl_cert_path, keyfile=ssl_key_path_encrypted, password=decrypted_password)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(cafile=ssl_cert_path)

        # Run the app
        app.run(host="0.0.0.0", port=8888, ssl_context=context, threaded=True, debug=True)
    except Exception as e:
        print(f"SSL Context Error: {e}")
        sys.exit(1)

