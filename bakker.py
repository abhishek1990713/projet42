from flask import Flask, jsonify, request
import ssl

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello, client! Connection is secure."})

if __name__ == '__main__':
    # SSL context configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.verify_mode = ssl.CERT_REQUIRED  # Require client certificate verification
    context.load_cert_chain(certfile='certificate.cer', keyfile='private.key')
    context.load_verify_locations(cafile='CA.pem')  # Load the CA certificate for client verification
    
    # Run the Flask app with SSL enabled
    app.run(host='127.0.0.1', port=8013, ssl_context=context)

# constant.py

# PaddleOCR model paths
DET_MODEL_DIR = r"C:\CitiDev\text_ocr\paddle_model\Multilingual_PP-OCRv3_det_infer"
REC_MODEL_DIR = r"C:\CitiDev\text_ocr\paddle_model\japan_PP-OCRv4_rec_infer"
CLS_MODEL_DIR = r"C:\CitiDev\text_ocr\paddle_model\ch_ppocr_mobile_v2.0_cls_infer"

# Passport model path
PASSPORT_MODEL_PATH = r"C:\CitiDev\japan_pipeline\all_model\passport_information.pt"

# Valid passport dates
VALID_ISSUE_DATE = "22 AUG 2010"
VALID_EXPIRY_DATE = "22 AUG 2029"
import logging
import re
from datetime import datetime
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
from yolov5 import YOLO
import constant  # Import constants

# Setup logging
logging.getLogger('ppocr').setLevel(logging.WARNING)

# Initialize PaddleOCR model
ocr = PaddleOCR(
    lang='japan',
    use_angle_cls=False,
    use_gpu=False,
    det=True,
    rec=True,
    cls=False,
    det_model_dir=constant.DET_MODEL_DIR,
    rec_model_dir=constant.REC_MODEL_DIR,
    cls_model_dir=constant.CLS_MODEL_DIR
)

# Parse valid date range
valid_issue_date = datetime.strptime(constant.VALID_ISSUE_DATE, "%d %b %Y")
valid_expiry_date = datetime.strptime(constant.VALID_EXPIRY_DATE, "%d %b %Y")

def process_passport_information(input_file_path):
    # Load YOLO model for passport detection
    model = YOLO(constant.PASSPORT_MODEL_PATH)
    
    # Run YOLO model on the input image
    results = model(input_file_path)
    
    # Open input image
    input_image = Image.open(input_file_path)

    date_of_issue = None
    date_of_expiry = None
    output = []  # To collect results for returning
    
    # Process results from YOLO model
    for result in results:
        boxes = result.boxes
        
        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]  # Get label from YOLO
            bbox = box.xyxy[0].tolist()  # Get bounding box coordinates

            # Crop the image to the detected box
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            cropped_image_np = np.array(cropped_image)

            # Perform OCR on the cropped image
            result_texts = ocr.ocr(cropped_image_np, cls=False)
            if result_texts and result_texts[0]:
                extracted_text = " ".join([text[1][0] for text in result_texts[0]])
            else:
                extracted_text = ""
            
            # Collect the detected label and extracted text
            output.append(f"Detected Label: {label}, Extracted Text: {extracted_text}")
            
            # Check for Date of Issue and Date of Expiry
            if label == "Date of issue":
                try:
                    date_of_issue = datetime.strptime(extracted_text, "%d %b %Y")
                    output.append(f"Extracted Date of Issue: {date_of_issue}")
                except ValueError:
                    output.append(f"Could not parse Date of Issue: {extracted_text}")
            
            elif label == "Date of expiry":
                try:
                    date_of_expiry = datetime.strptime(extracted_text, "%d %b %Y")
                    output.append(f"Extracted Date of Expiry: {date_of_expiry}")
                except ValueError:
                    output.append(f"Could not parse Date of Expiry: {extracted_text}")
    
    # Check if both dates were successfully extracted and validate them
    if date_of_issue and date_of_expiry:
        if valid_issue_date <= date_of_issue <= valid_expiry_date and date_of_expiry <= valid_expiry_date:
            output.append("Passport is valid within the given date range.")
        else:
            output.append("Passport dates do not fall within the valid range.")
    else:
        output.append("One or both dates could not be extracted or are invalid.")
    
    return output  # Return the collected results

# Example usage
input_file_path = r"path_to_your_image.jpg"
results = process_passport_information(input_file_path)

# Print the results
for res in results:
    print(res)
