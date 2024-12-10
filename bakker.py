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
# preprocess.py

# app.py

import cv2
import logging
from preprocess import process_image
from some_classification_module import predict_image_class  # Your model's classification import

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def process_image_pipeline(image_path, timeout=1806):
    result_log = {"processing_steps": []}

    try:
        result_log["processing_steps"].append(f"Processing started for image: {image_path}")
        logger.info(f"Processing started for image: {image_path}")

        # Read the image from the path
        image = cv2.imread(image_path)

        # Step 1: Preprocess the image (from preprocess.py)
        processed_image, metrics = process_image(image)
        result_log["processing_steps"].append("Image preprocessing completed.")
        logger.info("Image preprocessing completed.")
        
        # Add metrics to the result log
        result_log["metrics"] = metrics

        # Step 2: Classify the processed image
        result_log["processing_steps"].append("Proceeding with classification...")
        logger.info("Proceeding with classification...")

        # You can now call your classification model using the processed image
        model_path = "C:\\CitiDev\\japan_pipeline\\all_model\\classification_model.pt"
        classification_result = predict_image_class(model_path, processed_image)

        if classification_result:
            predicted_label = classification_result
            result_log["processing_steps"].append(f"Predicted Class: {predicted_label}")
            logger.info(f"Predicted Class: {predicted_label}")

    except Exception as e:
        result_log["error"] = str(e)
        logger.error(f"Error during processing: {e}")

    return result_log

# Example usage
image_path = "C:\\CitiDev\\japan_pipeline\\data_set\\Test image acr\\Picture1.png"
result = process_image_pipeline(image_path)

# Output the result
print(result)
