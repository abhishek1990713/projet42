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
import fitz  # PyMuPDF for PDF handling

# Threshold values for quality checks
THRESHOLD = {
    "blurriness": 50,
    "brightness": (50, 200),
    "contrast": 50,
    "noise_level": 30,
    "skew_angle": 5,
    "text_area": 20
}

# Function to convert an image to TIFF and ensure a minimum DPI
def convert_to_tif_with_dpi(image_path, output_path, min_dpi=300):
    print(f"Converting to TIFF: {image_path}")
    pil_image = Image.open(image_path)
    dpi = pil_image.info.get("dpi", (200, 200))[0]
    print(f"Current DPI: {dpi}")
    
    if dpi < min_dpi:
        print(f"DPI is lower than {min_dpi}. Adjusting DPI...")
        pil_image.save(output_path, dpi=(min_dpi, min_dpi))
    else:
        pil_image.save(output_path)
    print(f"Saved TIFF with DPI: {output_path}")
    return output_path

# Function to convert PDF to images (each page as TIFF)
def convert_pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)  # Open PDF
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img_array = np.array(pix.samples)  # Convert to numpy array (image)
        img_array = img_array.reshape((pix.height, pix.width, 4))  # reshape as RGBA image
        images.append(img_array)
    return images

# Function to check and adjust image brightness
def check_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    return brightness

def adjust_brightness(image, target=120):
    brightness = check_brightness(image)
    factor = target / brightness
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Brightness(pil_image)
    return cv2.cvtColor(np.array(enhancer.enhance(factor)), cv2.COLOR_RGB2BGR)

# Function to convert to black-and-white
def convert_to_black_and_white(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, bw_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(bw_image, cv2.COLOR_GRAY2BGR)

# Function to check blurriness
def check_blurriness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var

# Function to adjust blurriness
def adjust_blurriness(image):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

# Function to check skew angle
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
    return np.mean(angles) if angles else 0

# Function to deskew an image
def deskew_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# Function to process individual images
def process_image(image, file_name, output_path, quality_scores, output_folder):
    print(f"Processing Image: {file_name}")
    scores_before = {
        "blurriness": check_blurriness(image),
        "brightness": check_brightness(image),
        "skew_angle": check_skew_angle(image),
    }
    
    # Adjust quality metrics
    if scores_before["blurriness"] < THRESHOLD["blurriness"]:
        print("Adjusting blurriness...")
        image = adjust_blurriness(image)

    if not (THRESHOLD["brightness"][0] <= scores_before["brightness"] <= THRESHOLD["brightness"][1]):
        print("Adjusting brightness...")
        image = adjust_brightness(image)

    skew_angle = scores_before["skew_angle"]
    if abs(skew_angle) > THRESHOLD["skew_angle"]:
        print("Adjusting skew angle...")
        image = deskew_image(image, skew_angle)

    # Convert to black and white
    print("Converting to black-and-white...")
    image = convert_to_black_and_white(image)

    # Save final TIFF output
    print(f"Saving processed image: {output_path}")
    cv2.imwrite(output_path, image)

    # Log quality metrics after processing
    scores_after = {
        "blurriness": check_blurriness(image),
        "brightness": check_brightness(image),
        "skew_angle": check_skew_angle(image),
    }
    quality_scores.append({
        "Image": file_name,
        **{f"{k}_Before": v for k, v in scores_before.items()},
        **{f"{k}_After": v for k, v in scores_after.items()}
    })

# Main function to process files
def process_files(input_folder, output_folder, excel_path):
    os.makedirs(output_folder, exist_ok=True)
    quality_scores = []

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')):
            # Process image file
            tiff_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.tiff")
            convert_to_tif_with_dpi(file_path, tiff_path)
            image = cv2.imread(tiff_path)
            process_image(image, file_name, tiff_path, quality_scores, output_folder)

        elif file_name.lower().endswith('.pdf'):
            # Process PDF file
            print(f"Processing PDF: {file_name}")
            pdf_images = convert_pdf_to_images(file_path)
            for i, pdf_image in enumerate(pdf_images):
                pdf_image_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}_page_{i + 1}.tiff")
                # Process image (after conversion)
                process_image(pdf_image, file_name, pdf_image_path, quality_scores, output_folder)

    if quality_scores:
        df = pd.DataFrame(quality_scores)
        df.to_excel(excel_path, index=False)
        print(f"Quality metrics saved to: {excel_path}")

# Example usage
input_folder = r"C:\path\to\input"
output_folder = r"C:\path\to\output"
excel_path = os.path.join(output_folder, "quality_metrics.xlsx")

process_files(input_folder, output_folder, excel_path)
