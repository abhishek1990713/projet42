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

from ultralytics import YOLO
from ultralytics import YOLO
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
from datetime import datetime

# Initialize PaddleOCR for Japanese language
ocr = PaddleOCR(lang='japan', use_angle_cls=True)

# Define model path and input file path
model_path = "C:\\CitiDev\\text_ocr\\image_quality\\yolo_model\\src\\best.pt"
input_file_path = "C:\\CitiDev\\text_ocr\\image_quality\\yolo_model\\src\\japan_document.png"

# Define class names (for Japanese documents)
class_names = {
    0: 'Date_Of_Issue',
    1: 'Date_Of_Expiry',
    2: 'Name',
    3: 'Nationality',
    4: 'Passport_No'
}

# Condition for expiration date
valid_expiry_date = datetime.strptime("2028-08-22", "%Y-%m-%d")

# Load the YOLO model
model = YOLO(model_path)

# Perform inference on the input image
results = model(input_file_path)

# Load the input image using PIL
input_image = Image.open(input_file_path)

# Process results list
for result in results:
    boxes = result.boxes  # Bounding box outputs

    # Loop through each detected object
    for box in boxes:
        cls_id = int(box.cls[0])  # Class ID
        label = class_names.get(cls_id, "Unknown")  # Get label for the class ID
        bbox = box.xyxy[0].tolist()  # Get bounding box coordinates [x_min, y_min, x_max, y_max]

        # Crop the bounding box region from the input image
        cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

        # Convert PIL Image to numpy array for PaddleOCR compatibility
        cropped_image_np = np.array(cropped_image)

        # Perform OCR using PaddleOCR
        result_texts = ocr.ocr(cropped_image_np, cls=False)

        # Extract text
        extracted_text = " ".join([text[1][0] for text in result_texts[0]]) if result_texts else ""
        print(f"Detected {label}: {extracted_text}")

        # Apply condition for 'Date_Of_Expiry'
        if label == "Date_Of_Expiry":
            try:
                # Parse the expiration date in the detected text
                # Adjust the parsing to match the format of your detected text
                expiry_date = datetime.strptime(
                    extracted_text.replace("まで有宛", "").strip(), "%Y年%m月%d日"
                )
                if expiry_date < valid_expiry_date:
                    print(f"Expiration date {expiry_date.strftime('%Y-%m-%d')} is valid.")
                else:
                    print(f"Expiration date {expiry_date.strftime('%Y-%m-%d')} exceeds the valid range.")
            except ValueError:
                print("Could not parse the expiration date.")
