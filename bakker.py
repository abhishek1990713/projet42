import os
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time
import fitz  # PyMuPDF
import pandas as pd  # For DataFrame and Excel-like output

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


def save_to_excel(classification_df, details_df, output_filename):
    """Saves classification and details DataFrames to an Excel file."""
    with pd.ExcelWriter(output_filename) as writer:
        classification_df.to_excel(writer, sheet_name="Classification Result", index=False)
        details_df.to_excel(writer, sheet_name="Details", index=False)


def read_excel(output_filename):
    """Reads the Excel file and returns its content as DataFrames."""
    try:
        excel_data = pd.read_excel(output_filename, sheet_name=None)
        return excel_data
    except Exception as e:
        logger.exception(f"Failed to read Excel file {output_filename}: {str(e)}")
        return None


def process_image_pipeline(image_path, timeout=1800):
    """Processes an image, saves classification and details in an Excel file, then reads and returns it."""
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

                # Save DataFrames to Excel
                output_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}_result.xlsx"
                save_to_excel(classification_df, details_df, output_filename)
                logger.info(f"Results saved to: {output_filename}")

                # Read and return the Excel content
                excel_data = read_excel(output_filename)
                return excel_data

            else:
                return {"Error": "Image classification failed."}, None

        with ThreadPoolExecutor() as executor:
            future = executor.submit(process)
            result = future.result(timeout=timeout)

        logger.info(f"Processing completed for image: {image_path}")
        return result

    except TimeoutError:
        logger.error(f"Processing timed out for image: {image_path}")
        classification_df = create_dataframe("Error", "Processing timed out.")
        details_df = pd.DataFrame([["Error", "Timeout"]], columns=["Field", "Value"])
        save_to_excel(classification_df, details_df, "timeout_result.xlsx")
        excel_data = read_excel("timeout_result.xlsx")
        return excel_data

    except Exception as e:
        logger.exception(f"An error occurred while processing {image_path}: {str(e)}")
        classification_df = create_dataframe("Error", f"An error occurred: {str(e)}")
        details_df = pd.DataFrame([["Error", str(e)]], columns=["Field", "Value"])
        save_to_excel(classification_df, details_df, "error_result.xlsx")
        excel_data = read_excel("error_result.xlsx")
        return excel_data


# Example usage:
image_path = "/path/to/your/image.png"
output = process_image_pipeline(image_path)

# Display the returned output
if output:
    for sheet_name, sheet_data in output.items():
        print(f"\n{sheet_name} Sheet:")
        print(sheet_data.to_string(index=False))  # Print each sheet content
