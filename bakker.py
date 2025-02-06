
import os
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time
import fitz  # PyMuPDF
from prettytable import PrettyTable  # For table formatting

# Import functions for classification and processing
from yolo_classification_test import predict_image_class
from japan_keywords_file.rc_corner import process_rc_image
from japan_keywords_file.passport_corner import process_passport_image
from japan_keywords_file.driving_corner import process_dl_image
from japan_information_file.driving_lic_info import process_dl_information
from japan_information_file.rc_info import process_RC_information
from japan_information_file.passport_info import process_passport_information
from japan_information_file.inc_info import process_MNC_information

# Logging configuration
logging.basicConfig(
    filename="image_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


def create_table(title, data):
    """Creates a table from a dictionary or string data and returns it as a string."""
    table = PrettyTable()
    table.title = title
    table.field_names = ["Field", "Value"]

    if isinstance(data, dict):
        for key, value in data.items():
            table.add_row([key, value])
    elif isinstance(data, str):
        table.add_row(["Result", data])
    else:
        table.add_row(["Result", "Invalid data type"])

    return table.get_string()


def process_image_pipeline(image_path, timeout=1800):
    """Processes an image and returns classification and details as tables."""
    try:
        logger.info(f"Processing started for image: {image_path}")

        def process():
            logger.info("The image is sharp. Proceeding with classification...")
            model_path = r"/home/ko19678/japan_pipeline/japan_pipeline/all_model/classification_model.pt"
            classification_result = predict_image_class(model_path, image_path)

            if classification_result:
                classification_output = {"Classification": classification_result}
                details_output = {}

                if classification_result == 'Driving License':
                    process_result = process_dl_image(image_path)
                    if process_result == 'Image is not good.':
                        return create_table("Classification Result", "Image is not good."), None
                    details_output = process_dl_information(image_path)
                
                elif classification_result == 'Passport':
                    process_result = process_passport_image(image_path)
                    if process_result == 'Image is not good.':
                        return create_table("Classification Result", "Image is not good."), None
                    details_output = process_passport_information(image_path)

                elif classification_result == 'Residence Card':
                    process_result = process_rc_image(image_path)
                    if process_result == 'Image is not good.':
                        return create_table("Classification Result", "Image is not good."), None
                    details_output = process_RC_information(image_path)

                elif classification_result == 'MNC':
                    details_output = process_MNC_information(image_path)

                else:
                    return create_table("Classification Result", "Class not recognized for further processing."), None

                # Create tables for classification and details
                classification_table = create_table("Classification Result", classification_output)
                details_table = create_table("Details", details_output)

                return classification_table, details_table

            else:
                return create_table("Classification Result", "Image classification failed."), None

        with ThreadPoolExecutor() as executor:
            future = executor.submit(process)
            result = future.result(timeout=timeout)

        logger.info(f"Processing completed for image: {image_path}")
        return result

    except TimeoutError:
        logger.error(f"Processing timed out for image: {image_path}")
        return create_table("Error", "Processing timed out."), None

    except Exception as e:
        logger.exception(f"An error occurred while processing {image_path}: {str(e)}")
        return create_table("Error", f"An error occurred: {str(e)}"), None

