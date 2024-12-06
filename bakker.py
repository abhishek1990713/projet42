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

from datetime import datetime
import os
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import logging
import re
from ultralytics import YOLO  # Ensure you have the YOLO library installed

# Suppress PaddleOCR warnings
logging.getLogger('ppocr').setLevel(logging.WARNING)

# Model paths
det_model_dir = r"C:\CitiDev\text_ocr\paddle_model\Multilingual_PP-OCRv3_det_infer"
rec_model_dir = r"C:\CitiDev\text_ocr\paddle_model\japan_PP-OCRv4_rec_infer"
cls_model_dir = r"C:\CitiDev\text_ocr\paddle_model\ch_ppocr_mobile_v2.0_cls_infer"
driving_license_model_path = r"C:\CitiDev\text_ocr\image_quality\japan_pipeline\model\dl_information.pt"

# Expiry year range
min_expire_year = 2024
max_expire_year = 2028

# Initialize OCR
ocr = PaddleOCR(
    lang='japan',
    use_angle_cls=False,
    use_gpu=False,
    det=True,
    rec=True,
    cls=False,
    det_model_dir=det_model_dir,
    rec_model_dir=rec_model_dir,
    cls_model_dir=cls_model_dir
)

def process_dl_information(input_file_path):
    # Load YOLO model
    model = YOLO(driving_license_model_path)

    # Run YOLO model on the input image
    results = model(input_file_path)

    # Open the input image
    input_image = Image.open(input_file_path)

    # Store results
    extracted_data = []

    # Process YOLO results
    for result in results:
        boxes = result.boxes

        for box in boxes:
            cls_id = int(box.cls[0])
            label = result.names[cls_id]  # Get the label from YOLO results

            # Get bounding box coordinates
            bbox = box.xyxy[0].tolist()

            # Crop the detected area
            cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

            # Convert cropped image to numpy array for OCR
            cropped_image_np = np.array(cropped_image)

            # Perform OCR
            result_texts = ocr.ocr(cropped_image_np, cls=False)
            extracted_text = (
                " ".join([text[1][0] for text in result_texts[0]])
                if result_texts and result_texts[0]
                else ""
            )

            print(f"Detected Label: {label}, Extracted Text: {extracted_text}")

            # Check for expiration date
            year = None
            if label == "Expiration date":
                year_match = re.search(r"\d{4}年", extracted_text)
                if year_match:
                    year = int(year_match.group(0).replace("年", ""))
                    print(f"Extracted Year: {year}")
                    if min_expire_year <= year <= max_expire_year:
                        print(f"Year {year} is within the valid range ({min_expire_year}-{max_expire_year}).")
                    else:
                        print(f"Year {year} is outside the valid range ({min_expire_year}-{max_expire_year}).")
                else:
                    print("Year not found in 'Expiration date' text.")

            # Append results to the list
            extracted_data.append({
                "label": label,
                "text": extracted_text,
                "bbox": bbox,
                "year": year
            })

    # Return all extracted data
    return extracted_data

# Example usage
input_file_path = r"path_to_your_image.jpg"  # Replace with your input image path
result = process_dl_information(input_file_path)

# Print or process the results
for item in result:
    print(f"Label: {item['label']}, Text: {item['text']}, Year: {item['year']}, Bounding Box: {item['bbox']}")
