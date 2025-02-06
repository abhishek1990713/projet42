
import os
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time
import fitz  # PyMuPDF
import pandas as pd  # For DataFrame

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


def create_dataframe(title, data):
    """Creates a Pandas DataFrame from a dictionary or string data."""
    if isinstance(data, dict):
        df = pd.DataFrame(list(data.items()), columns=["Field", "Value"])
    elif isinstance(data, str):
        df = pd.DataFrame([["Result", data]], columns=["Field", "Value"])
    else:
        df = pd.DataFrame([["Result", "Invalid data type"]], columns=["Field", "Value"])
    return df


def print_dataframe(classification_df, details_df):
    """Prints the DataFrames to the console in a table format."""
    print("\nClassification Result:")
    print(classification_df.to_string(index=False))

    print("\nDetails:")
    print(details_df.to_string(index=False))


def process_image_pipeline(image_path, timeout=1800):
    """Processes an image and returns classification and details as DataFrames."""
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
                        return create_dataframe("Classification Result", "Image is not good."), None
                    details_output = process_dl_information(image_path)
                
                elif classification_result == 'Passport':
                    process_result = process_passport_image(image_path)
                    if process_result == 'Image is not good.':
                        return create_dataframe("Classification Result", "Image is not good."), None
                    details_output = process_passport_information(image_path)

                elif classification_result == 'Residence Card':
                    process_result = process_rc_image(image_path)
                    if process_result == 'Image is not good.':
                        return create_dataframe("Classification Result", "Image is not good."), None
                    details_output = process_RC_information(image_path)

                elif classification_result == 'MNC':
                    details_output = process_MNC_information(image_path)

                else:
                    return create_dataframe("Classification Result", "Class not recognized for further processing."), None

                # Create DataFrames for classification and details
                classification_df = create_dataframe("Classification Result", classification_output)
                details_df = create_dataframe("Details", details_output)

                # Print the DataFrames to the console
                print_dataframe(classification_df, details_df)
                return classification_df, details_df

            else:
                return create_dataframe("Classification Result", "Image classification failed."), None

        with ThreadPoolExecutor() as executor:
            future = executor.submit(process)
            result = future.result(timeout=timeout)

        logger.info(f"Processing completed for image: {image_path}")
        return result

    except TimeoutError:
        logger.error(f"Processing timed out for image: {image_path}")
        return create_dataframe("Error", "Processing timed out."), None

    except Exception as e:
        logger.exception(f"An error occurred while processing {image_path}: {str(e)}")
        return create_dataframe("Error", f"An error occurred: {str(e)}"), None
