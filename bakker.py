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

# Define constants for the model path and other parameters
import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance
import fitz  # PyMuPDF

# Threshold values for quality checks
THRESHOLD = {
    "blurriness": 50,
    "brightness": (50, 200),
    "contrast": 50,
    "noise_level": 30,
    "skew_angle": 5,
    "text_area": 20
}

# Function to convert image to black and white (grayscale)
def convert_to_black_and_white(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Function to calculate blurriness
def check_blurriness(image):
    gray = image
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var

# Function to adjust blurriness
def adjust_blurriness(image):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

# Function to calculate brightness
def check_brightness(image):
    brightness = np.mean(image)
    return brightness

# Function to adjust brightness
def adjust_brightness(image, target=120):
    brightness = check_brightness(image)
    factor = target / brightness
    pil_image = Image.fromarray(image)
    enhancer = ImageEnhance.Brightness(pil_image)
    return np.array(enhancer.enhance(factor))

# Function to calculate contrast
def check_contrast(image):
    contrast = np.std(image)
    return contrast

# Function to adjust contrast
def adjust_contrast(image, factor=1.5):
    pil_image = Image.fromarray(image)
    enhancer = ImageEnhance.Contrast(pil_image)
    return np.array(enhancer.enhance(factor))

# Function to calculate noise level
def check_noise_level(image):
    edges = cv2.Canny(image, 100, 200)
    noise_level = np.mean(edges)
    return noise_level

# Function to denoise image
def denoise_image(image):
    return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

# Function to calculate skew angle
def check_skew_angle(image):
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            angles.append(angle)
    skew_angle = np.mean(angles) if angles else 0
    return skew_angle

# Function to deskew image
def deskew_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# Function to calculate text area coverage
def check_text_area(image):
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    text_area = cv2.countNonZero(thresh)
    total_area = image.shape[0] * image.shape[1]
    coverage = (text_area / total_area) * 100
    return coverage

# Function to convert image to .tif format with desired DPI
def convert_to_tif_with_dpi(image_path, output_path, min_dpi=300):
    pil_image = Image.open(image_path)
    dpi = pil_image.info.get("dpi", (min_dpi, min_dpi))[0]  # Default to `min_dpi` if no DPI is found
    if dpi < min_dpi:
        pil_image = pil_image.resize(
            (int(pil_image.width * min_dpi / dpi), int(pil_image.height * min_dpi / dpi)),
            Image.Resampling.LANCZOS
        )
        dpi = min_dpi
    pil_image.save(output_path, format="TIFF", dpi=(dpi, dpi))
    return output_path

# Function to extract images from a PDF
def extract_images_from_pdf(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    extracted_images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap()
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(image_path)
        extracted_images.append(image_path)
    return extracted_images

# Quality check function
def quality_check(image_path):
    image = cv2.imread(image_path)
    image = convert_to_black_and_white(image)  # Convert image to black and white before checks
    metrics = {}
    metrics["blurriness"] = check_blurriness(image)
    metrics["brightness"] = check_brightness(image)
    metrics["contrast"] = check_contrast(image)
    metrics["noise_level"] = check_noise_level(image)
    metrics["skew_angle"] = check_skew_angle(image)
    metrics["text_area_coverage"] = check_text_area(image)
    return metrics

# Main processing function
def process_files(input_folder, output_folder, excel_path):
    os.makedirs(output_folder, exist_ok=True)
    quality_scores = []
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif', 'tif', 'pdf'))]

    for file in files:
        file_path = os.path.join(input_folder, file)

        if file.lower().endswith('.pdf'):
            # Process PDFs
            pdf_output_folder = os.path.join(output_folder, os.path.splitext(file)[0])
            os.makedirs(pdf_output_folder, exist_ok=True)
            extracted_images = extract_images_from_pdf(file_path, pdf_output_folder)
        else:
            # Process image files directly
            extracted_images = [file_path]

        for image_file in extracted_images:
            tif_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(image_file))[0]}.tif")
            convert_to_tif_with_dpi(image_file, tif_path)

            scores_before = quality_check(tif_path)
            image = cv2.imread(tif_path)

            if scores_before["blurriness"] < THRESHOLD["blurriness"]:
                image = adjust_blurriness(image)
            if not (THRESHOLD["brightness"][0] <= scores_before["brightness"] <= THRESHOLD["brightness"][1]):
                image = adjust_brightness(image)
            if scores_before["contrast"] < THRESHOLD["contrast"]:
                image = adjust_contrast(image)
            if scores_before["noise_level"] > THRESHOLD["noise_level"]:
                image = denoise_image(image)
            skew_angle = scores_before["skew_angle"]
            if abs(skew_angle) > THRESHOLD["skew_angle"]:
                image = deskew_image(image, skew_angle)

            cv2.imwrite(tif_path, image)
            scores_after = quality_check(tif_path)

            row = {
                "File": os.path.basename(file),
                "Image": os.path.basename(image_file),
                **{f"{metric}_Before": scores_before[metric] for metric in scores_before},
                **{f"{metric}_After": scores_after[metric] for metric in scores_after}
            }
            quality_scores.append(row)

    df = pd.DataFrame(quality_scores)
    df.to_excel(excel_path, index=False)
    print(f"Processed files saved to {output_folder}")
    print(f"Quality scores saved to {excel_path}")

# Example usage
input_folder = r"C:\path\to\input"
output_folder = r"C:\path\to\output"
excel_path = r"C:\path\to\output\quality_scores.xlsx"

process_files(input_folder, output_folder, excel_path)
