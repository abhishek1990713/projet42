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

# Define class names (assuming "Date_Of_Issue" is the only date field we need)
class_names = {0: 'Date_Of_Issue', 1: 'Name', 2: 'Nationality', 3: 'Passport_No'}

# Define validation date for the Date of Issue
valid_issue_date_start = datetime.strptime("22 Aug 2018", "%d %b %Y")

# Load the model
model = YOLO(model_path)

# Perform inference on the input image
results = model(input_file_path)

# Load the input image using PIL
input_image = Image.open(input_file_path)

# Initialize variable to store the Date of Issue
date_of_issue = None

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
        extracted_text = pytesseract.image_to_string(cropped_image, lang='jpn').strip()
        print(f"Detected {label}: {extracted_text}")

        # Parse the date if the detected field is Date of Issue
        if label == "Date_Of_Issue":
            try:
                # Adjust the date format as per Japanese format if needed
                date_of_issue = datetime.strptime(extracted_text, "%Y年%m月%d日")
            except ValueError:
                print(f"Could not parse Date of Issue: {extracted_text}")

    # Optionally, save or display the full annotated result
    result.show()  # Display result with bounding boxes
    result.save(filename="test_result.jpg")  # Save to disk

# Validate Date of Issue
if date_of_issue:
    if date_of_issue >= valid_issue_date_start:
        print("Document issue date is valid.")
    else:
        print("Document issue date is before the valid range.")
else:
    print("Date of Issue could not be extracted or is invalid.")
