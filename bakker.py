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
# api2_client.py

from ultralytics import YOLO
import os

def process_image(model_path, input_file_path, confidence_threshold=0.70, output_filename="test_result.jpg"):
    # Load the YOLO model
    model = YOLO(model_path)
    
    # Run the model on the input image
    results = model(input_file_path)
    
    # Flags to check conditions
    all_boxes_present = False
    confidence_check = False
    
    # Process results
    for result in results:
        # Extract bounding boxes and other outputs
        boxes = result.boxes  # Bounding boxes
        masks = result.masks  # Segmentation masks
        keypoints = result.keypoints  # Pose keypoints
        probs = result.probs  # Classification probabilities
        obb = result.obb  # Oriented bounding boxes
        
        # Show the result and save it
        result.show()  # Display on screen
        result.save(filename=output_filename)  # Save to disk
        print(f"Result saved as {output_filename}")
        
        # Check if required bounding boxes are present
        if boxes is not None and len(boxes) == 4:
            all_boxes_present = True
            print("All four bounding boxes are present.")
        else:
            print("Not all four bounding boxes are present.")
        
        # Check confidence scores
        confidence_scores = boxes.conf if boxes is not None else []
        if all(score >= confidence_threshold for score in confidence_scores):
            confidence_check = True
            print("All confidence scores are above the threshold of 0.70.")
        else:
            print("Some confidence scores are below the threshold of 0.70.")
    
    # Final check based on conditions
    if all_boxes_present and confidence_check:
        print("Image is uploaded correctly.")
    else:
        print("Image is not good.")

# Example usage
process_image(
    model_path=r"C:\CitiDev\DOC_OCR\Data_set\runs\detect\train\weights\best.pt",
    input_file_path=r"C:\CitiDev\Japne_classification\dataset\test_data\RC\v4na4xm1.png",
    confidence_threshold=0.70,
    output_filename="test_result.jpg"
)
