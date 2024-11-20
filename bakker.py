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
import fitz  # PyMuPDF for PDF processing

# Configure Logger
logging.basicConfig(
    filename="image_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()

def process_image(image_path, classifier, timeout=30):
    """Process a single image using the existing pipeline."""
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

def process_pdf(pdf_path, classifier, timeout=30):
    """Process a PDF by extracting pages and running the pipeline."""
    try:
        logger.info(f"Processing started for PDF: {pdf_path}")
        document = fitz.open(pdf_path)
        results = []

        for page_num in range(len(document)):
            # Convert each page to an image
            page = document.load_page(page_num)
            pix = page.get_pixmap()
            image_path = f"temp_page_{page_num + 1}.png"
            pix.save(image_path)

            # Process the extracted image
            logger.info(f"Processing page {page_num + 1} of {pdf_path}")
            result = process_image(image_path, classifier, timeout)
            results.append(f"Page {page_num + 1}: {result}")

            # Remove the temporary image file
            os.remove(image_path)

        return "\n".join(results)

    except Exception as e:
        logger.exception(f"Error processing PDF {pdf_path}: {e}")
        return "An error occurred during PDF processing."

def process_input_file(file_path, classifier, timeout=30):
    """Determine if the input is an image or PDF and process accordingly."""
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return process_image(file_path, classifier, timeout)
    elif file_path.lower().endswith('.pdf'):
        return process_pdf(file_path, classifier, timeout)
    else:
        return "Unsupported file format. Please provide an image or PDF."

# Model path and class indices
model_path = r"C:\CitiDev\text_ocr\image_quality\japan_pipeline\model\inception_v3_model_newtrain_japan.h5"
class_indices = {0: 'driving license', 1: 'others', 2: 'passport', 3: 'residence_card'}

# Initialize the classifier
classifier = ImageClassifier(model_path, class_indices)

# Example file path (image or PDF)
file_path = r"C:\CitiDev\text_ocr\image_quality\japan_pipeline\Test image\example_file.pdf"

# Process the input file
result_message = process_input_file(file_path, classifier)
print(result_message)
