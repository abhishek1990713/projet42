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
from PIL import Image
import pytesseract
from datetime import datetime

# Define model path and input file path
model_path = "C:\\CitiDev\\text_ocr\\image_quality\\yolo_model\\src\\best.pt"
input_file_path = "C:\\CitiDev\\text_ocr\\image_quality\\yolo_model\\src\\bge9m4lu.png"

# Define class names
class_names = {0: 'Date_Of_Issue', 1: 'Date_Of_Expiry', 2: 'Name', 3: 'Nationality', 4: 'Passport_No'}

# Define date validation parameters
valid_issue_date = datetime.strptime("22 Aug 2018", "%d %b %Y")
valid_expiry_date = datetime.strptime("22 Aug 2028", "%d %b %Y")

# Load the model
model = YOLO(model_path)

# Perform inference on the input image
results = model(input_file_path)

# Load the input image using PIL
input_image = Image.open(input_file_path)

# Initialize variables to store date values
date_of_issue = None
date_of_expiry = None

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
        cropped_image.show(title=label)  # Display the cropped region

        # Perform OCR on the cropped image
        extracted_text = pytesseract.image_to_string(cropped_image).strip()
        print(f"Detected {label}: {extracted_text}")

        # Parse dates if the detected field is Date of Issue or Date of Expiry
        if label == "Date_Of_Issue":
            try:
                date_of_issue = datetime.strptime(extracted_text, "%d %b %Y")
            except ValueError:
                print(f"Could not parse Date of Issue: {extracted_text}")
        
        elif label == "Date_Of_Expiry":
            try:
                date_of_expiry = datetime.strptime(extracted_text, "%d %b %Y")
            except ValueError:
                print(f"Could not parse Date of Expiry: {extracted_text}")

    # Optionally, save or display the full annotated result
    result.show()  # Display result with bounding boxes
    result.save(filename="test_result.jpg")  # Save to disk

# Validate dates based on the conditions provided
if date_of_issue and date_of_expiry:
    if valid_issue_date <= date_of_issue <= valid_expiry_date and date_of_expiry <= valid_expiry_date:
        print("Passport is valid within the given date range.")
    else:
        print("Passport dates do not fall within the valid range.")
else:
    print("One or both dates could not be extracted or are invalid.")
