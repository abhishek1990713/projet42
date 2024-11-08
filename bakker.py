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
from ultralytics import YOLO
import os
import re
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
import logging

# Set logging level for PaddleOCR
logging.getLogger('ppocr').setLevel(logging.WARNING)

class PassportOCR:
    def __init__(self, model_path, det_model_dir, rec_model_dir, cls_model_dir, temp_fld_path, confidence_threshold=0.70):
        # Initialize model paths
        self.det_model_dir = det_model_dir
        self.rec_model_dir = rec_model_dir
        self.cls_model_dir = cls_model_dir
        
        # Initialize OCR
        self.ocr = PaddleOCR(lang='japan', use_angle_cls=False, use_gpu=False, det=True, rec=True, cls=False,
                             det_model_dir=self.det_model_dir, rec_model_dir=self.rec_model_dir, cls_model_dir=self.cls_model_dir)
        
        # YOLO model path
        self.model_path = model_path
        
        # File paths
        self.temp_fld_path = temp_fld_path
        self.confidence_threshold = confidence_threshold
        
        # Initialize YOLO model
        self.model = YOLO(self.model_path)
    
    def process_image(self, input_file_path):
        file_name = os.path.basename(input_file_path)
        
        # Load the YOLO model and process the image
        results = self.model(input_file_path)
        image = Image.open(input_file_path)
        
        # Flags to check conditions
        all_boxes_present = False
        confidence_check = False
        passport_code_check = False
        
        for result in results:
            boxes = result.boxes
            confidence_scores = [box.conf[0].item() for box in boxes] if boxes is not None else []
            
            # Check if all bounding boxes are present
            if boxes is not None and len(boxes) == 4:
                all_boxes_present = True
                print("All four bounding boxes are present.")
            else:
                print("Not all four bounding boxes are present.")
            
            # Check confidence scores
            if all(score >= self.confidence_threshold for score in confidence_scores):
                confidence_check = True
                print("All confidence scores are above the threshold of 0.70.")
            else:
                print("Some confidence scores are below the threshold of 0.70.")
            
            # Check for valid passport code
            for box in boxes:
                class_id = result.names[box.cls[0].item()]
                if class_id == "Bottom":
                    cords = box.xyxy[0].tolist()
                    cords = [round(x) for x in cords]
                    imcrop = image.crop((cords[0], cords[1], cords[2], cords[3]))
                    
                    temp_file = file_name.split(".")[0]
                    temp_file_name = os.path.join(self.temp_fld_path, f"{temp_file}_crop_{class_id}.png")
                    imcrop.save(temp_file_name)
                    
                    # Convert PIL Image to NumPy array and perform OCR
                    imcrop_np = np.array(imcrop)  # Convert to NumPy array
                    ocr_text = self.ocr.ocr(imcrop_np, cls=True)  # OCR with PaddleOCR
                    
                    print("OCR Text:", ocr_text)
                    
                    # Validate passport code
                    pattern = r"^[A-Za-z]{2}.*\d{2}$"
                    match = re.match(pattern, ocr_text[0][0][1])  # Assuming the text is in the first element of the result
                    if match:
                        print("Valid passport code")
                        passport_code_check = True
                    else:
                        print("Invalid passport code")
        
        # Final check based on conditions
        if all_boxes_present and confidence_check and passport_code_check:
            print("Image is uploaded correctly")
        else:
            print("Image is not good")

# Usage example
det_model_dir = r"C:\CitiDev\text_ocr\paddle_model\Multilingual_PP-OCRv3_det_infer"
rec_model_dir = r"C:\CitiDev\text_ocr\paddle_model\japan_PP-OCRv4_rec_infer"
cls_model_dir = r"C:\CitiDev\text_ocr\paddle_model\ch_ppocr_mobile_v2.0_cls_infer"
model_path = r"C:\CitiDev\text_ocr\image_quality\yolo_model\best_passport.pt"
temp_fld_path = r"C:\CitiDev\text_ocr\image_quality\yolo_model\temp"

passport_ocr = PassportOCR(model_path=model_path, 
                           det_model_dir=det_model_dir, 
                           rec_model_dir=rec_model_dir, 
                           cls_model_dir=cls_model_dir, 
                           temp_fld_path=temp_fld_path)

input_file_path = r"C:\CitiDev\text_ocr\image_quality\test_data\augmented_me_bge9m4lu.png"
passport_ocr.process_image(input_file_path)
