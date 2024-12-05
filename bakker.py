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
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import fitz  # PyMuPDF for PDF to image conversion
import pandas as pd

# Quality thresholds for image processing
THRESHOLD = {
    "blurriness": 50,
    "brightness": (50, 200),
    "contrast": 50,
    "noise_level": 30,
    "skew_angle": 5
}

# Function to calculate blurriness
def check_blurriness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# Function to adjust blurriness
def adjust_blurriness(image):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

# Function to calculate brightness
def check_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

# Function to adjust brightness
def adjust_brightness(image, target=120):
    brightness = check_brightness(image)
    factor = target / brightness
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Brightness(pil_image)
    return cv2.cvtColor(np.array(enhancer.enhance(factor)), cv2.COLOR_RGB2BGR)

# Function to calculate contrast
def check_contrast(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.std(gray)

# Function to adjust contrast
def adjust_contrast(image, factor=1.5):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Contrast(pil_image)
    return cv2.cvtColor(np.array(enhancer.enhance(factor)), cv2.COLOR_RGB2BGR)

# Function to calculate noise level
def check_noise_level(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return np.mean(edges)

# Function to denoise image
def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

# Function to calculate skew angle
def check_skew_angle(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angles.append(np.degrees(theta) - 90)
    return np.mean(angles) if angles else 0

# Function to deskew image
def deskew_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# Function to convert image to black and white
def convert_to_black_and_white(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Convert image to TIFF format with DPI adjustment
def convert_to_tif_with_dpi(image_path, output_path, min_dpi=300):
    print(f"Converting {image_path} to TIFF format with minimum DPI of {min_dpi}...")
    pil_image = Image.open(image_path)
    dpi = pil_image.info.get("dpi", (200, 200))[0]
    if dpi < min_dpi:
        print(f"DPI is less than {min_dpi}. Adjusting DPI...")
        pil_image = pil_image.convert("RGB")
        pil_image.save(output_path, format="TIFF", dpi=(min_dpi, min_dpi))
    else:
        pil_image.save(output_path, format="TIFF", dpi=(dpi, dpi))

# Convert PDF to images (one TIFF per page)
def convert_pdf_to_images(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    image_paths = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{page_num + 1}.tiff")
        pix.save(img_path, "TIFF")
        image_paths.append(img_path)
    return image_paths

# Process all files in input folder
def process_files(input_folder, output_folder, excel_path):
    os.makedirs(output_folder, exist_ok=True)
    quality_scores = []

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        # Process images
        if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')):
            tiff_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.tiff")
            convert_to_tif_with_dpi(file_path, tiff_path)
            image = cv2.imread(tiff_path)
            process_image(image, file_name, tiff_path, quality_scores, output_folder)

        # Process PDFs
        elif file_name.lower().endswith('.pdf'):
            print(f"Processing PDF: {file_name}")
            pdf_image_paths = convert_pdf_to_images(file_path, output_folder)
            for pdf_image_path in pdf_image_paths:
                image = cv2.imread(pdf_image_path)
                process_image(image, os.path.basename(pdf_image_path), pdf_image_path, quality_scores, output_folder)

    # Save quality scores to Excel
    if quality_scores:
        df = pd.DataFrame(quality_scores)
        df.to_excel(excel_path, index=False)
        print(f"Quality metrics saved to: {excel_path}")

# Process individual image
def process_image(image, file_name, save_path, quality_scores, output_folder):
    print(f"Processing {file_name}...")

    image_bw = convert_to_black_and_white(image)

    # Quality scoring
    scores = {
        "blurriness": check_blurriness(image_bw),
        "brightness": check_brightness(image_bw),
        "contrast": check_contrast(image_bw),
        "noise_level": check_noise_level(image_bw),
        "skew_angle": check_skew_angle(image_bw)
    }

    # Adjustments based on quality scores
    if scores["blurriness"] < THRESHOLD["blurriness"]:
        image_bw = adjust_blurriness(image_bw)
    if not THRESHOLD["brightness"][0] <= scores["brightness"] <= THRESHOLD["brightness"][1]:
        image_bw = adjust_brightness(image_bw)
    if scores["contrast"] < THRESHOLD["contrast"]:
        image_bw = adjust_contrast(image_bw)
    if scores["noise_level"] > THRESHOLD["noise_level"]:
        image_bw = denoise_image(image_bw)
    if abs(scores["skew_angle"]) > THRESHOLD["skew_angle"]:
        image_bw = deskew_image(image_bw, scores["skew_angle"])

    # Save final processed image as TIFF
    final_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}_processed.tiff")
    cv2.imwrite(final_path, image_bw)
    print(f"Final processed image saved to: {final_path}")

    quality_scores.append({"file_name": file_name, **scores})

# Example usage
input_folder = "path_to_input_folder"  # Folder containing images and PDFs
output_folder = "path_to_output_folder"  # Folder where processed files will be saved
excel_path = "path_to_quality_metrics.xlsx"  # Path to save the quality metrics
process_files(input_folder, output_folder, excel_path)
