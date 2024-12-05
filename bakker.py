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

import os
from ultralytics import YOLO
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the classification function
def classify_image(image_path, model_path):
    model = YOLO(model_path)

    # Predict the result
    results = model.predict(source=image_path)
    
    # Store final results
    final_result = []

    # Process each result
    for result in results:
        predicted_label = result.names[result.probs.top1]
        confidence = result.probs.topiconf

        # Print and log results
        print(f"File Name: {os.path.basename(result.path)}")
        print(f"Predicted Class: {predicted_label}")
        print(f"Confidence Score: {confidence:.2f}")

        # Log the result
        logger.info(f"Predicted Class: {predicted_label} (Confidence: {confidence:.2f})")

        final_result.append([os.path.basename(result.path), predicted_label, f'{confidence:.2f}'])

    return final_result

# Example usage
image_path = r'C:\CitiDev\japan_pipeline\data_set\Test image\6f7rch30.png'
model_path = r"C:\CitiDev\japan_pipeline\all_model\classification_model.pt"
classification_result = classify_image(image_path, model_path)

# Check the predicted label and take action
if classification_result:
    predicted_label = classification_result[0][1]  # Extract the predicted label
    confidence = float(classification_result[0][2])  # Extract the confidence

    print(f"Predicted Class: {predicted_label} (Confidence: {confidence:.2f})")
    
    if predicted_label == 'driving license':
        # Implement any additional logic for 'driving license'
        pass
