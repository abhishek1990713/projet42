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
import numpy as np
from PIL import Image
import logging
from keras.models import load_model
from brisque import BRISQUE
from allmodel_test import ImageClassifier
from japan_kayords import process_dl_image, process_rc_image, process_passport_image
from japan_information import process_dl_information, process_Passport_information, process_RC_information
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time

# Configure Logger
logging.basicConfig(
    filename="image_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()

def process_image_pipeline(image_path, classifier, timeout=30):
    try:
        logger.info(f"Processing started for image: {image_path}")

        def process():
            img = Image.open(image_path)
            img_ndarray = np.asarray(img)

            # Check image quality using BRISQUE
            obj = BRISQUE(url=False)
            score = obj.score(img_ndarray)

            if score >= 60:
                return "The image quality is not good and cannot be processed."

            classification_result = classifier.predict(image_path)

            if classification_result:
                predicted_label = classification_result['predicted_label']
                confidence = classification_result['confidence']

                if predicted_label == 'driving license':
                    output = process_dl_image(image_path)
                    if output == 'Image is not good.':
                        return "Driving license image quality is not sufficient."
                    return process_dl_information(image_path)

                elif predicted_label == 'passport':
                    output = process_passport_image(image_path)
                    if output == 'Image is not good.':
                        return "Passport image quality is not sufficient."
                    return process_Passport_information(image_path)

                elif predicted_label == 'residence_card':
                    output = process_rc_image(image_path)
                    if output == 'Image is not good.':
                        return "Residence card image quality is not sufficient."
                    return process_RC_information(image_path)

                else:
                    return "Class not recognized for processing."
            else:
                return "Image classification failed."

        # Run the process with a timeout
        with ThreadPoolExecutor() as executor:
            future = executor.submit(process)
            result = future.result(timeout=timeout)

        return result

    except TimeoutError:
        return "Processing timed out."

    except Exception as e:
        logger.exception(f"Error processing image {image_path}: {e}")
        return "An error occurred during processing."

# Model path and class indices
model_path = r"C:\CitiDev\text_ocr\image_quality\japan_pipeline\model\inception_v3_model_newtrain_japan.h5"
class_indices = {0: 'driving license', 1: 'others', 2: 'passport', 3: 'residence_card'}

# Initialize the classifier
classifier = ImageClassifier(model_path, class_indices)

# Example image path
image_path = r"C:\CitiDev\text_ocr\image_quality\japan_pipeline\Test image\augmented_me_bge9m4lu.png"

# Process the image
result_message = process_image_pipeline(image_path, classifier)
print(result_message)
