

import fitz  # PyMuPDF
import cv2
import numpy as np
import os
from scipy.ndimage import interpolation as inter
import aspose.ocr as ocr

# Instantiate Aspose.OCR API
api = ocr.AsposeOCR()

# Define folders
TEMP_FOLDER = r"C:\temp\pdf_pages"
OUTPUT_FOLDER = r"C:\temp\output"
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def correct_skew(image, angle):
    """ Rotates the image to correct skew """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected

def extract_pdf_pages(pdf_path):
    """ Extracts pages from PDF and saves them as high-resolution images """
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File '{pdf_path}' not found.")
        return []

    try:
        pdf_document = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Error: Cannot open PDF - {e}")
        return []

    saved_images = []

    for page_num in range(len(pdf_document)):
        print(f"Extracting page {page_num + 1}...")

        # Convert PDF page to high-resolution image
        zoom_x, zoom_y = 2.0, 2.0  # Increase resolution
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = pdf_document[page_num].get_pixmap(matrix=mat)

        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

        # Convert to BGR format for OpenCV
        if pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif pix.n == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # Save temporary image
        temp_image_path = os.path.join(TEMP_FOLDER, f"Page_{page_num + 1}.png")
        cv2.imwrite(temp_image_path, img)
        saved_images.append(temp_image_path)

    return saved_images

def process_images(image_paths):
    """ Processes extracted images and saves corrected versions """
    for image_path in image_paths:
        print(f"Processing {image_path}...")

        # Perform skew detection using Aspose.OCR
        try:
            ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
            ocr_input.add(image_path)
            angles = api.calculate_skew(ocr_input)
        except RuntimeError as e:
            print(f"⚠ Warning: Skew detection failed for {image_path} - {e}")
            continue

        # Load image with OpenCV
        img = cv2.imread(image_path)

        if angles and img is not None:
            skew_angle = angles[0].angle  # Get skew angle
            print(f"{image_path}: Skew Angle Detected = {skew_angle:.2f}°")
            img = correct_skew(img, -skew_angle)  # Correct skew

            # Apply adaptive thresholding for better text visibility
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                              cv2.THRESH_BINARY, 11, 2)
            img = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        else:
            print(f"{image_path}: No skew detected")

        # Save corrected image in output folder
        output_image_path = os.path.join(OUTPUT_FOLDER, os.path.basename(image_path))
        cv2.imwrite(output_image_path, img)
        print(f"✅ Skew-corrected image saved at: {output_image_path}")

if __name__ == "__main__":
    # File path
    file_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\Skewed- Payment advice.pdf"

    if file_path.lower().endswith(".pdf"):
        images = extract_pdf_pages(file_path)  # Extract pages as images
        process_images(images)  # Process and correct skew for each image
    else:
        print("❌ Error: Please provide a PDF file.")
