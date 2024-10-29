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
import ssl
import os
from flask import Flask
from configobj import ConfigObj
from constant import CONFIG_FILE, PARAMETER, THREADS, LOCAL_HOST, LOG_LEVEL, PORT_NO

app = Flask(__name__)

# Load configuration
config = ConfigObj(CONFIG_FILE)
threads = int(config[PARAMETER][THREADS])
port_no = int(config[PARAMETER][PORT_NO])

# Define paths for certificates
server_crt_path = "path/to/certificate.cer"
server_key_path = "path/to/private_key.key"
ca_crt_path = "path/to/ca_certificate.cer"

def get_ssl_context(server_crt_path=server_crt_path, server_key_path=server_key_path, ca_crt_path=ca_crt_path):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.verify_mode = ssl.CERT_REQUIRED  # Set to CERT_NONE if client verification is not needed
    ssl_context.check_hostname = False
    ssl_context.load_verify_locations(ca_crt_path)
    ssl_context.load_cert_chain(certfile=server_crt_path, keyfile=server_key_path)
    return ssl_context

@app.route('/')
def home():
    return "Hello, SSL-secured Flask!"

def main():
    host = LOCAL_HOST
    port = port_no or (443 if os.getenv('ENVIRONMENT') == 'production' else 80)
    
    # SSL Context
    ssl_context = get_ssl_context()
    
    # Run Flask app with SSL
    app.run(host=host, port=port, ssl_context=ssl_context, threaded=True)

if __name__ == "__main__":
    main()
