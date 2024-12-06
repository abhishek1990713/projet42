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
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from yolo_classification_test import predict_image_class
from japan_keywords_file.rc_corner import process_rc_image
from japan_keywords_file.passport_corner import process_passport_image
from japan_keywords_file.driving_corner import process_dl_image
from japan_information_file.driving_lic_info import process_dl_information
from japan_information_file.rc_info import process_RC_information
from japan_information_file.passport_info import process_Passport_information
from japan_information_file.Mnc_info import process_MNC_information

logging.basicConfig(
    filename="image_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger()


def process_image_pipeline(image_path, timeout=1800):
    result_log = {"processing_steps": []}

    try:
        result_log["processing_steps"].append(f"Processing started for image: {image_path}")
        logger.info(f"Processing started for image: {image_path}")

        def process():
            result_log["processing_steps"].append("The image is sharp. Proceeding with classification...")
            logger.info("The image is sharp. Proceeding with classification...")

            model_path = r"C:\CitiDev\japan_pipeline\all_model\classification_model.pt"
            classification_result = predict_image_class(model_path, image_path)

            if classification_result:
                predicted_label = classification_result
                result_log["processing_steps"].append(f"Predicted Class: {predicted_label}")

                if predicted_label == 'Driving License':
                    process_result = process_dl_image(image_path)
                    if process_result == 'Image is not good.':
                        return {"error": "Image is not good."}

                    result_log["processing_steps"].append("Processing result: All four bounding boxes are present")
                    result_log["processing_steps"].append("Processing result: All confidence scores are above the threshold of 0.7.")
                    result_log["processing_steps"].append("Processing result: Image quality is good and all corners match.")

                    details = process_dl_information(image_path)
                    result_log["details"] = details
                    return result_log

                elif predicted_label == 'Passport':
                    process_result = process_passport_image(image_path)
                    if process_result == 'Image is not good.':
                        return {"error": "Image is not good."}

                    details = process_Passport_information(image_path)
                    result_log["details"] = details
                    return result_log

                elif predicted_label == 'Residence Card':
                    process_result = process_rc_image(image_path)
                    if process_result == 'Image is not good.':
                        return {"error": "Image is not good."}

                    details = process_RC_information(image_path)
                    result_log["details"] = details
                    return result_log

                elif predicted_label == 'MNC':
                    details = process_MNC_information(image_path)
                    result_log["details"] = details
                    return result_log

                else:
                    return {"error": "Class not recognized for further processing."}
            else:
                return {"error": "Image classification failed."}

        with ThreadPoolExecutor() as executor:
            future = executor.submit(process)
            result = future.result(timeout=timeout)
            logger.info(f"Processing completed for image: {image_path}")
            return result

    except TimeoutError:
        logger.error(f"Processing timed out for image: {image_path}")
        return {"error": "Processing timed out."}

    except Exception as e:
        logger.exception(f"An error occurred while processing {image_path}: {str(e)}")
        return {"error": f"An error occurred during processing: {str(e)}"}
