import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from yolo_classification_test import predict_image_class
from japan_keywords_file.rc_corner import process_rc_image
from japan_keywords_file.passport_corner import process_passport_image
from japan_keywords_file.driving_corner import process_dl_image
from japan_information_file.driving_lic_info import process_dl_information
from japan_information_file.rc_info import process_RC_information
from japan_information_file.passport_info import process_passport_information
from japan_information_file.Mac_info import process_MNC_information
import pandas as pd
import time
import fitz

# Logging configuration
logging.basicConfig(
    filename="image_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

def process_image_pipeline(image_path, timeout=1800):
    table_data = []

    try:
        logger.info(f"Processing started for image: {image_path}")

        def process():
            logger.info("The image is sharp. Proceeding with classification...")

            model_path = "/home/ko19678/japan_pipeline/japan_pipeline/all_model/classification_model.pt"
            classification_result = predict_image_class(model_path, image_path)

            if classification_result:
                table_data.append(["Classification", classification_result])
                logger.info(f"Predicted Class: {classification_result}")

                if classification_result == 'Driving License':
                    details = process_dl_information(image_path)
                    format_details(table_data, details, "Driving License")

                elif classification_result == 'Passport':
                    details = process_passport_information(image_path)
                    format_details(table_data, details, "Passport")

                elif classification_result == 'Residence Card':
                    details = process_RC_information(image_path)
                    format_details(table_data, details, "Residence Card")

                elif classification_result == 'MNC':
                    details = process_MNC_information(image_path)
                    format_details(table_data, details, "MNC")

                else:
                    table_data.append(["Error", "Class not recognized for further processing."])
            else:
                table_data.append(["Error", "Image classification failed."])

        with ThreadPoolExecutor() as executor:
            future = executor.submit(process)
            future.result(timeout=timeout)

        logger.info(f"Processing completed for image: {image_path}")
        print_table(table_data)
        return table_data

    except TimeoutError:
        logger.error(f"Processing timed out for image: {image_path}")
        table_data.append(["Error", "Processing timed out."])
        print_table(table_data)
        return table_data

    except Exception as e:
        logger.exception(f"An error occurred while processing {image_path}: {str(e)}")
        table_data.append(["Error", f"An error occurred: {str(e)}"])
        print_table(table_data)
        return table_data


def format_details(table_data, details, doc_type):
    """
    Format extracted details into table data.
    Handles pandas.Series values properly.
    """
    table_data.append(["Document Type", doc_type])
    
    for key, value in details.items():
        if isinstance(value, pd.Series):
            value = ", ".join(value.astype(str))  # Convert Series to comma-separated string
        table_data.append([key, value if pd.notna(value) else "N/A"])


def print_table(table_data):
    """
    Print the results in a table format.
    """
    print(f"{'Label':<30} {'Extracted Text':<50}")
    print("-" * 80)
    for row in table_data:
        print(f"{row[0]:<30} {row[1]:<50}")


# Example function call
if __name__ == "__main__":
    image_path = "/path/to/your/image.jpg"  # Replace with the actual image path
    process_image_pipeline(image_path)


