from flask import Flask, jsonify, request
import ssl

import os
import json
import logging
from translation import initialize_models, translate_text
from yolo_classification_test import predict_image_class
from japan_keywords_file.rc_corner import process_rc_image
from japan_keywords_file.passport_corner import process_passport_image
from japan_keywords_file.driving_corner import process_dl_image
from japan_information_file.driving_lic_info import process_dl_information
from japan_information_file.rc_info import process_RC_information
from japan_information_file.passport_info import process_passport_information
from japan_information_file.inc_info import process_MNC_information
from image_quality.Preprocessing import process_image

# Logging Configuration
logging.basicConfig(
    filename="image_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger()

def process_image_pipeline(image_path, lang_model, translation_pipeline, target_language="en"):
    """Process the image and handle classification and translation."""
    result_log = {"processing_steps": []}
    try:
        result_log["processing_steps"].append(f"Processing started for image: {image_path}")
        logger.info(f"Processing started for image: {image_path}")

        # Step 1: Preprocess Image
        processed_image, metrics = process_image(image_path)
        result_log["metrics"] = metrics
        result_log["processing_steps"].append("Image preprocessing completed.")

        # Step 2: Classify Image
        model_path = r"C:\CitiDev\japan_pipeline\all_model\classification_model.pt"
        classification_result = predict_image_class(model_path, processed_image)
        result_log["processing_steps"].append("Image classification completed.")
        if not classification_result:
            return {"error": "Image classification failed."}

        predicted_label = classification_result
        result_log["processing_steps"].append(f"Predicted Class: {predicted_label}")

        # Step 3: Process Image Based on Classification
        if predicted_label == "Driving License":
            process_result = process_dl_image(image_path)
            details = process_dl_information(image_path)
        elif predicted_label == "Passport":
            process_result = process_passport_image(image_path)
            details = process_passport_information(image_path)
        elif predicted_label == "Residence Card":
            process_result = process_rc_image(image_path)
            details = process_RC_information(image_path)
        elif predicted_label == "MNC":
            details = process_MNC_information(image_path)
        else:
            return {"error": "Class not recognized for further processing."}

        if "Image is not good." in process_result:
            return {"error": "Image quality is poor."}

        result_log["details"] = details

        # Step 4: Translate Details
        translated_details = translate_text(details, lang_model, translation_pipeline, target_language)
        result_log["translated_details"] = translated_details
        result_log["processing_steps"].append("Translation completed.")
        logger.info(f"Processing completed for image: {image_path}")

        return result_log
    except Exception as e:
        logger.error(f"Error processing image: {image_path}. Error: {e}")
        return {"error": f"An error occurred: {e}"}

if __name__ == "__main__":
    # Initialize Translation Models
    lang_model_path = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
    translation_model_path = r"C:\CitiDev\language_prediction\m2m"
    lang_model, translation_pipeline = initialize_models(lang_model_path, translation_model_path)

    # Input File
    image_path = r"C:\CitiDev\text_ocr\image_quality\japan_pipeline\Test_image\ocr\Picture1.png"
    result_message = process_image_pipeline(image_path, lang_model, translation_pipeline, target_language="en")
    print(json.dumps(result_message, indent=4, ensure_ascii=False))
