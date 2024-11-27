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
import logging
from datetime import datetime
from PIL import Image
import numpy as np
from ultralytics import YOLO
import pytesseract

logging.basicConfig(level=logging.WARNING)

# Set paths
valid_issue_date = datetime.strptime("22 AUG 2010", "%d %b %Y")
valid_expiry_date = datetime.strptime("22 AUG 2029", "%d %b %Y")

def process_passport_information(input_file_path):
    model_path = r"C:\Users\AS34751\Downloads\best.pt"
    model = YOLO(model_path)

    # Load the image
    results = model(input_file_path)
    input_image = Image.open(input_file_path)

    date_of_issue = None
    date_of_expiry = None

    for result in results:
        boxes = result.boxes
        result.show()

        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]
            bbox = box.xyxy[0].tolist()

            # Crop the detected region
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

            # Convert the cropped image to numpy array for OCR
            cropped_image_np = np.array(cropped_image)

            # Perform OCR using PyTesseract
            extracted_text = pytesseract.image_to_string(cropped_image_np, lang="eng").strip()

            print(f"Detected {label}: {extracted_text}")

            # Parse dates if applicable
            if label == "Date of issue":
                try:
                    date_of_issue = datetime.strptime(extracted_text, "%d %b %Y")
                except ValueError:
                    print(f"Could not parse Date of Issue: {extracted_text}")
            elif label == "Date of expiry":
                try:
                    date_of_expiry = datetime.strptime(extracted_text, "%d %b %Y")
                except ValueError:
                    print(f"Could not parse Date of Expiry: {extracted_text}")

    # Print results
    print(f"Date of Issue: {date_of_issue}")
    print(f"Date of Expiry: {date_of_expiry}")

# Example usage
process_passport_information(r"C:\path_to_your_image\passport_image.jpg")
