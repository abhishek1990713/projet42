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

def process_dl_information(input_file_path):
    # Load YOLO model
    model = YOLO(driving_license_model_path)

    # Run YOLO model on the input image
    results = model(input_file_path)

    # Open the input image
    input_image = Image.open(input_file_path)

    output = []  # To store results

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

            output.append(f"Detected Label: {label}, Extracted Text: {extracted_text}")

            # Check for expiration date
            if label == "Expiration date":
                year_match = re.search(r"\d{4}年", extracted_text)
                if year_match:
                    year = int(year_match.group(0).replace("年", ""))
                    output.append(f"Extracted Year: {year}")
                    if min_expire_year <= year <= max_expire_year:
                        output.append(f"Year {year} is within the valid range ({min_expire_year}-{max_expire_year}).")
                    else:
                        output.append(f"Year {year} is outside the valid range ({min_expire_year}-{max_expire_year}).")
                else:
                    output.append("Year not found in 'Expiration date' text.")

    return output  # Return the collected results

# Example usage
input_file_path = r"path_to_your_image.jpg"
results = process_dl_information(input_file_path)
for res in results:
    print(res)
