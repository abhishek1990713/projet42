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

from flask import Flask, jsonify
import ssl

app = Flask(__name__)

# Endpoint for testing
@app.route("/")
def root():
    return jsonify({"message": "Hello from API 1 - Secured with mTLS"})

# Configure SSL context with server and client certificate verification
def create_ssl_context():
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    # Path to the server certificate and private key
    ssl_context.load_cert_chain(certfile="path/to/server_cert.cer", keyfile="path/to/server_key.key")
    
    # Disable verification of client certificates since we don't have a CA cert
    ssl_context.verify_mode = ssl.CERT_OPTIONAL  # You can use CERT_REQUIRED if you want to enforce client certs

    return ssl_context

if __name__ == "__main__":
    ssl_context = create_ssl_context()
    app.run(host="0.0.0.0", port=8000, ssl_context=ssl_context)




import requests

# Path to the client certificate and private key
client_cert = ("path/to/client_cert.cer", "path/to/client_key.key")
# Since we don't have a CA cert, we'll use `verify=False` to skip server certificate verification
response = requests.get("https://api1.example.com/", cert=client_cert, verify=False)

# Display the response
print(response.json())
