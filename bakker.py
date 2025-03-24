
import fitz  # PyMuPDF
import cv2
import numpy as np
import os
from scipy.ndimage import interpolation as inter
import aspose.ocr as ocr

# Instantiate Aspose.OCR API
api = ocr.AsposeOCR()

# Define output directory
OUTPUT_FOLDER = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Create folder if not exists

def correct_skew(image, angle):
    """ Rotates the image to correct skew """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected

def process_pdf(file_path):
    """ Processes multi-page PDF and saves each page as a separate corrected image """
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    try:
        pdf_document = fitz.open(file_path)
    except Exception as e:
        print(f"❌ Error: Cannot open PDF - {e}")
        return

    for page_num in range(len(pdf_document)):
        print(f"Processing page {page_num + 1}...")

        # Convert PDF page to image
        pix = pdf_document[page_num].get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        # Convert RGB to BGR (for OpenCV)
        if pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        # Save temporary image
        temp_image_path = os.path.join(OUTPUT_FOLDER, f"temp_page_{page_num + 1}.jpg")
        cv2.imwrite(temp_image_path, img)

        # Perform skew detection using AsposeOCR
        try:
            ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
            ocr_input.add(temp_image_path)  
            angles = api.calculate_skew(ocr_input)
        except RuntimeError as e:
            print(f"⚠ Warning: Skew detection failed on page {page_num + 1} - {e}")
            continue

        if angles:
            skew_angle = angles[0].angle  # Get skew angle for this page
            print(f"Page {page_num + 1}: Skew Angle Detected = {skew_angle:.2f}°")
            img = correct_skew(img, -skew_angle)  # Correct skew
        else:
            print(f"Page {page_num + 1}: No skew detected")

        # Save corrected page as a separate image
        output_image_path = os.path.join(OUTPUT_FOLDER, f"Corrected_Page_{page_num + 1}.png")
        cv2.imwrite(output_image_path, img)
        print(f"✅ Skew-corrected image saved at: {output_image_path}")

if __name__ == "__main__":
    # File path
    file_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\Skewed- Payment advice.pdf"

    if file_path.lower().endswith(".pdf"):
        process_pdf(file_path)
    else:
        print("❌ Error: Please provide a PDF file.")
