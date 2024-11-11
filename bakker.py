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
import socket
import ssl
import requests

# Paths to the client certificate and private key, along with the password for the private key
CERTFILE = 'certificate.pem'   # Path to the client certificate
KEYFILE = 'private.key'        # Path to the client private key
KEY_PASSWORD = 'your_password_here'  # Password for the private key (replace with actual password)
SERVER_CERT = 'server_cert.pem'  # Path to the server's certificate (optional for testing)

# Flask server URL
url = 'https://127.0.0.1:8443/api/data'

# Send a GET request with the client certificate for mTLS (using requests with cert and key)
try:
    # Using requests to connect securely with the server, bypassing the verification of the server certificate.
    response = requests.get(
        url,
        cert=(CERTFILE, KEYFILE),  # Client cert and key for mTLS
        verify=SERVER_CERT  # Verify the server certificate (if you have it, or set to False for testing)
    )
    print("Response from server:", response.json())
except requests.exceptions.SSLError as e:
    print("SSL error:", e)
except Exception as e:
    print("Error:", e)

# For direct SSL socket connection without using requests (handling raw SSL sockets)
try:
    # Create SSL context and configure it
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    # Load the client certificate and private key with a password for the private key
    context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE, password=KEY_PASSWORD)
    
    # Optionally, disable hostname checking and server certificate verification for testing
    context.check_hostname = False  # Disable hostname checking (optional)
    
    # Specify the server's certificate (if using self-signed or custom CA)
    context.load_verify_locations(cafile=SERVER_CERT)  # If the server's certificate is not trusted by default

    # Establish connection to Flask server
    with socket.create_connection(('127.0.0.1', 8443)) as sock:
        with context.wrap_socket(sock, server_hostname='127.0.0.1') as ssock:
            print("Connected to server securely (using specified server cert).")
            ssock.sendall(b"Hello, server")
            data = ssock.recv(1024)
            print("Received:", data.decode())
except Exception as e:
    print("Socket error:", e)
