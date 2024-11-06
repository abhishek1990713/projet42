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



from paddleocr import PPStructure, draw_structure_result
from PIL import Image
import os

# Set paths to the pre-downloaded models
detection_model_dir = r'C:\path\to\local\en_PP-OCRv3_det_infer'  # Detection model path
layout_model_dir = r'C:\path\to\local\ppyolov2_r50vd_dcn_365e_voc'  # Layout model path

# Initialize PPStructure with local model paths for offline layout analysis
layout_engine = PPStructure(
    show_log=True,
    det_model_dir=detection_model_dir,  # Set detection model directory
    structure_model_dir=layout_model_dir,  # Set layout model directory
    use_angle_cls=True,  # Angle classification if needed
    lang='en'  # Language option
)

# Set the image path
image_path = r'C:\path\to\your\image.jpg'

# Perform layout analysis
result = layout_engine(image_path)

# Set up the output directory
output_dir = r'C:\path\to\output'
os.makedirs(output_dir, exist_ok=True)

# Load the image for visualization
image = Image.open(image_path).convert('RGB')

# Process each layout element and save results
for i, element in enumerate(result):
    if 'img' in element:
        # Save element image if it contains an image (e.g., table)
        element_img_path = os.path.join(output_dir, f'element_{i}.jpg')
        element['img'].save(element_img_path)
    else:
        # Draw and save bounding boxes for text, title, table, list
        draw_img = draw_structure_result(image, [element])
        draw_img_path = os.path.join(output_dir, f'element_{i}_layout.jpg')
        draw_img.save(draw_img_path)

    # Print details of each element
    print(f"Element {i+1}: Type - {element['type']}, Bounding box - {element['bbox']}")

print("Offline layout analysis completed. Results saved in the output directory.")
