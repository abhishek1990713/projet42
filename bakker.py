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
from PyPDF2 import PdfReader
from io import BytesIO

# Threshold values for quality checks
THRESHOLD = {
    "blurriness": 50,
    "brightness": (50, 200),
    "contrast": 50,
    "noise_level": 30,
    "skew_angle": 5,
    "text_area": 20
}

# Function to convert image to .tif format with the specified DPI (default is 300)
def convert_to_tif_with_dpi(image_path, output_path, min_dpi=300):
    print("Checking image properties...")

    # Open the image with PIL (Pillow)
    pil_image = Image.open(image_path)

    # Get current DPI from the image (default to (200, 200) if not available)
    dpi = pil_image.info.get("dpi", (200, 200))[0]

    print(f"Current DPI: {dpi}")

    # Get the current dimensions (width and height) of the image
    width, height = pil_image.size
    print(f"Current Dimensions: {width}x{height}")

    adjustments_made = False

    # Check if DPI is less than the desired minimum DPI
    if dpi < min_dpi:
        print(f"DPI is lower than {min_dpi}. Adjusting DPI to {min_dpi}...")
        
        # Adjust the DPI by resizing the image to meet the desired DPI
        pil_image = pil_image.resize(
            (int(pil_image.width * min_dpi / dpi), int(pil_image.height * min_dpi / dpi)),
            Image.Resampling.LANCZOS
        )
        dpi = min_dpi  # Set DPI to the minimum DPI after resizing
        adjustments_made = True

    # Save the image as TIFF with the adjusted DPI
    pil_image.save(output_path, format="TIFF", dpi=(dpi, dpi))

    # Confirm adjustments
    if adjustments_made:
        print(f"Image adjusted to {dpi} DPI and saved as {output_path}")
    else:
        print(f"No DPI adjustment needed. Image saved as {output_path}")

    return output_path

# Convert image to black and white
def convert_to_black_and_white(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Function to calculate blurriness
def check_blurriness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var

# Function to adjust blurriness
def adjust_blurriness(image):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

# Function to calculate brightness
def check_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    return brightness

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
    contrast = np.std(gray)
    return contrast

# Function to adjust contrast
def adjust_contrast(image, factor=1.5):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Contrast(pil_image)
    return cv2.cvtColor(np.array(enhancer.enhance(factor)), cv2.COLOR_RGB2BGR)

# Function to calculate noise level
def check_noise_level(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    noise_level = np.mean(edges)
    return noise_level

# Function to denoise image
def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

# Function to calculate skew angle
def check_skew_angle(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
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
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    text_area = cv2.countNonZero(thresh)
    total_area = image.shape[0] * image.shape[1]
    coverage = (text_area / total_area) * 100
    return coverage

# Function to crop text area
def crop_text_area(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = cv2.findNonZero(thresh)
    x, y, w, h = cv2.boundingRect(coords)
    return image[y:y+h, x:x+w]

# Quality check function
def quality_check(image_path):
    image = cv2.imread(image_path)
    metrics = {}
    metrics["blurriness"] = check_blurriness(image)
    metrics["brightness"] = check_brightness(image)
    metrics["contrast"] = check_contrast(image)
    metrics["noise_level"] = check_noise_level(image)
    metrics["skew_angle"] = check_skew_angle(image)
    metrics["text_area_coverage"] = check_text_area(image)
    return metrics

# Function to handle PDFs
def process_pdf(pdf_path, output_folder):
    pdf_reader = PdfReader(pdf_path)
    for page_num, page in enumerate(pdf_reader.pages):
        print(f"Processing page {page_num + 1} of {pdf_path}...")
        image = page.to_image(resolution=300)  # Convert PDF page to image at 300 DPI
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        image.save(image_path, "PNG")
        convert_to_tif_with_dpi(image_path, os.path.join(output_folder, f"page_{page_num + 1}.tif"))
        os.remove(image_path)  # Delete the temporary PNG image

# Main processing function
def process_images(input_folder, output_folder, excel_path):
    os.makedirs(output_folder, exist_ok=True)
    images = [f for f in os.listdir(input_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    pdfs = [f for f in os.listdir(input_folder) if f.lower().endswith('pdf')]
    
    quality_scores = []

    for image_file in images:
        image_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, image_file)
        image = cv2.imread(image_path)

        # Convert to black and white
        image = convert_to_black_and_white(image)

        # Convert to TIFF with DPI adjustment if needed
        convert_to_tif_with_dpi(image_path, output_path, min_dpi=300)

        # Quality checks before adjustments
        scores_before = quality_check(image_path)

        # Apply adjustments based on thresholds
        if scores_before["blurriness"] < THRESHOLD["blurriness"]:
            image = adjust_blurriness(image)
        if not (THRESHOLD["brightness"][0] <= scores_before["brightness"] <= THRESHOLD["brightness"][1]):
            image = adjust_brightness(image)
        if scores_before["contrast"] < THRESHOLD["contrast"]:
            image = adjust_contrast(image)
        if scores_before["noise_level"] > THRESHOLD["noise_level"]:
            image = denoise_image(image)
        if abs(scores_before["skew_angle"]) > THRESHOLD["skew_angle"]:
            image = deskew_image(image, scores_before["skew_angle"])

        # Save the adjusted image
        cv2.imwrite(output_path, image)

        # Quality checks after adjustments
        scores_after = quality_check(output_path)
        quality_scores.append({image_file: {"before": scores_before, "after": scores_after}})

    # Process PDFs
    for pdf_file in pdfs:
        pdf_path = os.path.join(input_folder, pdf_file)
        process_pdf(pdf_path, output_folder)

    # Save quality metrics to Excel
    quality_df = pd.DataFrame(quality_scores)
    quality_df.to_excel(excel_path, index=False)

# Main execution
if __name__ == "__main__":
    input_folder = "path_to_input_folder"  # Path to the folder containing images and PDFs
    output_folder = "path_to_output_folder"  # Path to save the output images
    excel_path = "path_to_quality_metrics.xlsx"  # Path to save the quality metrics
    process_images(input_folder, output_folder, excel_path)
