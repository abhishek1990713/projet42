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

import re
from ultralytics import YOLO
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR

# Initialize PaddleOCR for Japanese language
ocr = PaddleOCR(lang='japan')

# Define model path and input file path
model_path = "C:\\CitiDev\\text_ocr\\image_quality\\yolo_model\\src\\best.pt"
input_file_path = "C:\\CitiDev\\text_ocr\\image_quality\\yolo_model\\src\\japan_document.png"

# Expiration year condition
min_expire_year = 2024
max_expire_year = 2028

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
    for i, box in enumerate(boxes):
        cls_name = result.names[int(box.cls[0])]  # Dynamically predict the class name
        bbox = box.xyxy[0].tolist()  # Get bounding box coordinates [x_min, y_min, x_max, y_max]

        # Crop the bounding box region from the input image
        cropped_image = input_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

        # Convert PIL Image to numpy array for PaddleOCR compatibility
        cropped_image_np = np.array(cropped_image)

        # Perform OCR using PaddleOCR
        result_texts = ocr.ocr(cropped_image_np, cls=False)

        # Extract text
        extracted_text = " ".join([text[1][0] for text in result_texts[0]]) if result_texts else ""

        print(f"Detected {cls_name}: {extracted_text}")

        # Apply the expiration year condition only to "Date of Expire"
        if cls_name == "Date of Expire":  # Ensure the class name matches dynamically detected name
            # Use regex to extract only the year (e.g., '2024年')
            year_match = re.search(r"\d{4}年", extracted_text)
            if year_match:
                year = int(year_match.group(0).replace("年", ""))  # Extract year as an integer
                print(f"Extracted Year: {year}")

                # Validate expiration year
                if min_expire_year <= year <= max_expire_year:
                    print(f"Year {year} is within the valid range ({min_expire_year}-{max_expire_year}).")
                else:
                    print(f"Year {year} is outside the valid range ({min_expire_year}-{max_expire_year}).")
            else:
                print("Year not found in 'Date of Expire'.")
