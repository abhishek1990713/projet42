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
import cv2
import numpy as np
import os
import pytesseract
import pandas as pd
from sklearn import metrics

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to adjust brightness and contrast
def adjust_brightness_contrast(image, brightness=0, contrast=0):
    image = np.int16(image)
    image = image * (contrast / 127 + 1) - contrast + brightness
    image = np.clip(image, 0, 255)
    return np.uint8(image)

# Function to denoise image
def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

# Function to blur image
def blur_image(image):
    return cv2.GaussianBlur(image, (5, 5), 0)

# Function to apply thresholding
def apply_threshold(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return thresh

# Function to apply morphological operations
def morphological_operations(image):
    kernel = np.ones((3, 3), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    return image

# Function to calculate image metrics
def calculate_metrics(image):
    metrics = {}
    metrics['image_size'] = f"{image.shape[1]} x {image.shape[0]}"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    noise_estimation = np.std(image)
    metrics['blurriness'] = laplacian_var
    metrics['noise_level'] = noise_estimation
    return metrics

# Function to check if image is colored
def is_colored(image):
    if len(image.shape) == 2:
        return False
    elif len(image.shape) == 3:
        b, g, r = cv2.split(image)
        return not (np.array_equal(b, g) and np.array_equal(b, r))
    else:
        raise ValueError("Unsupported image format")

# Function to extract text using Tesseract OCR
def extract_text_with_tesseract(image, lang='eng'):
    try:
        config = "--psm 3"
        text = pytesseract.image_to_string(image, config=config, lang=lang)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

# Function to calculate image size in human-readable format
def get_image_size(file_path):
    size_in_bytes = os.path.getsize(file_path)
    size_in_kb = size_in_bytes / 1024
    size_in_mb = size_in_kb / 1024
    if size_in_mb >= 1:
        return f"{size_in_mb:.2f} MB"
    else:
        return f"{size_in_kb:.2f} KB"

# Function to calculate PSNR between two images
def calculate_psnr(original, processed):
    mse = np.mean((original - processed) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 10 * np.log10((max_pixel ** 2) / mse)
    return psnr

# Function to save metrics to an Excel file
def save_metrics_to_excel(metrics_list, excel_path):
    df = pd.DataFrame(metrics_list)
    df.to_excel(excel_path, index=False, engine='openpyxl')
    print(f"Metrics saved to: {excel_path}")

# Main function to process images
def process_image_from_folder(input_folder, output_dir, excel_path, ocr_lang="eng"):
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    image_paths = [os.path.join(input_folder, file) for file in os.listdir(input_folder) if file.lower().endswith(valid_extensions)]
    
    if not image_paths:
        raise ValueError(f"No image file found in the folder: {input_folder}")
    
    post_output_dir = os.path.join(output_dir, "PostProcessed")
    os.makedirs(post_output_dir, exist_ok=True)
    metric_list = []

    for image_path in image_paths:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}. Skipping...")
            continue
        
        try:
            print(f"Processing image: {image_path}")
            image_name = os.path.basename(image_path)
            original_size = get_image_size(image_path)
            
            # Pre-metrics
            pre_metrics = calculate_metrics(image)
            pre_metrics['image_name'] = image_name
            pre_metrics['original_size'] = original_size
            
            if is_colored(image):
                print("Image is colored. Applying preprocessing...")
                denoised = denoise_image(image)
                adjusted = adjust_brightness_contrast(denoised, brightness=30, contrast=30)
                preprocessed = adjusted
            else:
                print("Image is black-and-white. Applying preprocessing...")
                blurred = blur_image(image)
                preprocessed = apply_threshold(blurred)
            
            # Morphological operations
            morphed = morphological_operations(preprocessed)
            processed_image_path = os.path.join(post_output_dir, f"processed_{image_name}")
            cv2.imwrite(processed_image_path, morphed)
            
            # Post-processing metrics
            post_metrics = calculate_metrics(morphed)
            post_metrics['image_name'] = image_name
            post_metrics['processed_size'] = get_image_size(processed_image_path)
            post_metrics['psnr'] = f"{calculate_psnr(image, morphed):.2f} dB"
            
            # OCR
            ocr_text = extract_text_with_tesseract(morphed, lang=ocr_lang)
            ocr_text_path = os.path.join(post_output_dir, f"{os.path.splitext(image_name)[0]}.txt")
            with open(ocr_text_path, 'w', encoding="utf-8") as f:
                f.write(ocr_text)
            print(f"OCR result saved for {image_name} at: {ocr_text_path}")
            
            # Combine pre and post metrics for Excel
            combined_metrics = {**{'pre_' + k: v for k, v in pre_metrics.items()},
                                **{'post_' + k: v for k, v in post_metrics.items()}}
            metric_list.append(combined_metrics)
        except Exception as e:
            print(f"Error processing image: {image_path}. Error: {e}")
            continue
    
    # Save metrics to Excel
    if metric_list:
        save_metrics_to_excel(metric_list, excel_path)
        print("Batch processing completed. Metrics saved to Excel.")
    else:
        print("No image processed successfully.")

# Define paths
input_folder = r"C:\CitiDev\preprocessing\Input"
output_dir = r"C:\CitiDev\preprocessing\Output"
excel_path = r"C:\CitiDev\preprocessing\Xlsx\metrics.xlsx"
ocr_lang = 'eng'

# Process images
process_image_from_folder(input_folder, output_dir, excel_path, ocr_lang)
