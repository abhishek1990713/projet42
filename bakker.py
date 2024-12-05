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
from PIL import Image
import fitz  # PyMuPDF
import numpy as np

# Convert PDF pages to images (TIFF format)
def convert_pdf_to_images(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()

        # Save the image as a PNG (temporary step before TIFF conversion)
        temp_img_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{page_num + 1}.png")
        pix.save(temp_img_path)

        # Convert the PNG to TIFF using Pillow
        tiff_img_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{page_num + 1}.tiff")
        with Image.open(temp_img_path) as img:
            img.save(tiff_img_path, format="TIFF")

        # Remove the temporary PNG file
        os.remove(temp_img_path)

        image_paths.append(tiff_img_path)

    return image_paths

# Convert an image to black and white
def convert_to_bw(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Adjust DPI of the image if it's less than 300
def adjust_dpi(image_path, output_path, min_dpi=300):
    print(f"Converting {image_path} to TIFF format with minimum DPI of {min_dpi}...")
    pil_image = Image.open(image_path)
    dpi = pil_image.info.get("dpi", (200, 200))[0]
    print(f"Current DPI: {dpi}")

    if dpi < min_dpi:
        print(f"DPI is less than {min_dpi}. Adjusting DPI...")
        pil_image.save(output_path, format="TIFF", dpi=(min_dpi, min_dpi))
        print(f"Image adjusted to {min_dpi} DPI and saved as {output_path}")
    else:
        pil_image.save(output_path, format="TIFF", dpi=(dpi, dpi))
        print(f"Image DPI is already {dpi}, saved as {output_path}")

# Check blurriness of the image
def check_blurriness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance

# Check brightness of the image
def check_brightness(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    brightness = np.mean(hsv[:, :, 2])
    return brightness

# Process the image with various transformations
def process_image(image, file_name, output_folder):
    print(f"Processing {file_name}...")
    
    # Convert to black and white
    image_bw = convert_to_bw(image)
    print(f"Image {file_name} converted to black and white.")

    # Adjust DPI (save as TIFF with adjusted DPI)
    tiff_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}_adjusted.tiff")
    adjust_dpi(tiff_path, tiff_path)

    # Check blurriness and brightness
    blurriness = check_blurriness(image_bw)
    brightness = check_brightness(image_bw)

    print(f"Blurriness: {blurriness}")
    print(f"Brightness: {brightness}")

    return tiff_path, blurriness, brightness

# Process files (both PDFs and images)
def process_files(input_folder, output_folder):
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"Processing image: {file_name}")
            image = cv2.imread(file_path)
            process_image(image, file_name, output_folder)

        elif file_name.lower().endswith('.pdf'):
            print(f"Processing PDF: {file_name}")
            pdf_image_paths = convert_pdf_to_images(file_path, output_folder)
            for pdf_image_path in pdf_image_paths:
                image = cv2.imread(pdf_image_path)
                process_image(image, os.path.basename(pdf_image_path), output_folder)

# Main function to start the processing
if __name__ == "__main__":
    input_folder = "input"  # Your input folder path
    output_folder = "output"  # Your output folder path

    process_files(input_folder, output_folder)
