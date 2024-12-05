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

# Function to convert image to TIFF format
def convert_to_tif_with_dpi(image_path, output_path, min_dpi=300):
    print("Checking image properties...")
    pil_image = Image.open(image_path)
    dpi = pil_image.info.get("dpi", (200, 200))[0]
    print(f"Current DPI: {dpi}")
    width, height = pil_image.size
    print(f"Current Dimensions: {width}x{height}")

    # Adjust DPI if needed
    adjustments_made = False
    if dpi < min_dpi:
        print(f"DPI is lower than {min_dpi}. Adjusting DPI to {min_dpi}...")
        pil_image.save(output_path, dpi=(min_dpi, min_dpi))
        adjustments_made = True
    else:
        pil_image.save(output_path, dpi=(dpi, dpi))

    print(f"Image saved as {output_path}")
    return output_path

# Function to convert PDF to images (each page as image)
def convert_pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)  # Open PDF
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        
        # Convert pixmap to numpy array (pix.samples returns RGBA values)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8)
        
        # Handle images with different channels (RGBA, RGB, Grayscale)
        if pix.n < 4:  # For grayscale or RGB images
            img_array = img_array.reshape((pix.height, pix.width, pix.n))  # Reshape accordingly
        else:
            img_array = img_array.reshape((pix.height, pix.width, 4))  # RGBA format
        
        # Convert RGBA to BGR (OpenCV uses BGR format)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR) if pix.n == 4 else img_array
        images.append(img_bgr)
    
    return images

# Function to convert image to black and white
def convert_to_black_and_white(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, bw_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return bw_image

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
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    text_area = cv2.countNonZero(thresh)
    total_area = image.shape[0] * image.shape[1]
    coverage = (text_area / total_area) * 100
    return coverage

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

# Main processing function
def process_files(input_folder, output_folder, excel_path):
    os.makedirs(output_folder, exist_ok=True)
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'pdf'))]
    quality_scores = []
    
    for file in files:
        file_path = os.path.join(input_folder, file)
        
        # Process PDFs
        if file.lower().endswith('pdf'):
            print(f"Processing PDF: {file}")
            pdf_images = convert_pdf_to_images(file_path)
            for page_num, image in enumerate(pdf_images):
                image_path = os.path.join(output_folder, f"{file}_page_{page_num + 1}.tif")
                image = convert_to_black_and_white(image)
                image = convert_to_tif_with_dpi(image, image_path)
                scores_before = quality_check(image_path)
                # Apply adjustments
                image = adjust_blurriness(image) if scores_before["blurriness"] < THRESHOLD["blurriness"] else image
                image = adjust_brightness(image) if not (THRESHOLD["brightness"][0] <= scores_before["brightness"] <= THRESHOLD["brightness"][1]) else image
                image = adjust_contrast(image) if scores_before["contrast"] < THRESHOLD["contrast"] else image
                image = denoise_image(image) if scores_before["noise_level"] > THRESHOLD["noise_level"] else image
                skew_angle = scores_before["skew_angle"]
                if abs(skew_angle) > THRESHOLD["skew_angle"]:
                    image = deskew_image(image, skew_angle)
                cv2.imwrite(image_path, image)
                scores_after = quality_check(image_path)
                row = {
                    "File": file,
                    "Page": page_num + 1,
                    **{f"{metric}_Before": scores_before[metric] for metric in scores_before},
                    **{f"{metric}_After": scores_after[metric] for metric in scores_after}
                }
                quality_scores.append(row)
        
        # Process images
        elif file.lower().endswith(('png', 'jpg', 'jpeg')):
            print(f"Processing image: {file}")
            image = cv2.imread(file_path)
            image = convert_to_black_and_white(image)
            image_path = os.path.join(output_folder, f"{file}.tif")
            image = convert_to_tif_with_dpi(image, image_path)
            scores_before = quality_check(image_path)
            # Apply adjustments
            image = adjust_blurriness(image) if scores_before["blurriness"] < THRESHOLD["blurriness"] else image
            image = adjust_brightness(image) if not (THRESHOLD["brightness"][0] <= scores_before["brightness"] <= THRESHOLD["brightness"][1]) else image
            image = adjust_contrast(image) if scores_before["contrast"] < THRESHOLD["contrast"] else image
            image = denoise_image(image) if scores_before["noise_level"] > THRESHOLD["noise_level"] else image
            skew_angle = scores_before["skew_angle"]
            if abs(skew_angle) > THRESHOLD["skew_angle"]:
                image = deskew_image(image, skew_angle)
            cv2.imwrite(image_path, image)
            scores_after = quality_check(image_path)
            row = {
                "File": file,
                "Page": 1,
                **{f"{metric}_Before": scores_before[metric] for metric in scores_before},
                **{f"{metric}_After": scores_after[metric] for metric in scores_after}
            }
            quality_scores.append(row)

    # Save results to Excel
    df = pd.DataFrame(quality_scores)
    df.to_excel(excel_path, index=False)
    print(f"Quality scores saved to {excel_path}")

# Example usage
input_folder = 'path_to_input_folder'
output_folder = 'path_to_output_folder'
excel_path = 'path_to_save_quality_scores.xlsx'
process_files(input_folder, output_folder, excel_path)
