

import fitz  # PyMuPDF
import cv2
import numpy as np
import os
from scipy.ndimage import interpolation as inter
import aspose.ocr as ocr
from PIL import Image

# Instantiate Aspose.OCR API
api = ocr.RecognitionEngine()

# Change temp path to a writable directory
TEMP_DIR = os.path.join(os.environ.get('TEMP', '.'), "skew_correction")
os.makedirs(TEMP_DIR, exist_ok=True)


def correct_skew(image, angle):
    """Rotates the image to correct skew"""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected


def process_pdf(file_path, output_pdf_path):
    """Processes a multi-page PDF for skew detection and correction"""
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    try:
        pdf_document = fitz.open(file_path)
    except Exception as e:
        print(f"❌ Error: Cannot open PDF '{file_path}' - {e}")
        return

    output_images = []

    for page_num in range(len(pdf_document)):
        print(f"Processing page {page_num + 1} of {os.path.basename(file_path)}...")

        # Convert PDF page to image
        pix = pdf_document[page_num].get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

        if pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        # Save temporary image
        temp_image_path = os.path.join(TEMP_DIR, f"page_{page_num + 1}.jpg")
        cv2.imwrite(temp_image_path, img)

        # Perform skew detection using AsposeOCR
        try:
            ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
            ocr_input.add(temp_image_path)
            angles = api.calculate_skew(ocr_input)
        except RuntimeError as e:
            print(f"⚠️ Warning: Skew detection failed on page {page_num + 1} - {e}")
            continue

        if angles:
            skew_angle = angles[0].angle  # Get skew angle for this page
            print(f"Page {page_num + 1}: Skew Angle Detected = {skew_angle:.2f}")
            img = correct_skew(img, skew_angle)  # Correct skew
        else:
            print(f"Page {page_num + 1}: No skew detected")

        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        output_images.append(img_pil)

    if output_images:
        # Save all corrected pages as a new PDF
        output_images[0].save(output_pdf_path, save_all=True, append_images=output_images[1:])
        print(f"✅ Skew-corrected PDF saved at: {output_pdf_path}")


def process_all_pdfs(input_folder, output_folder):
    """Processes all PDFs in the input folder and saves output in the output folder"""
    if not os.path.exists(input_folder):
        print(f"❌ Error: Input folder '{input_folder}' not found.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️ No PDF files found in '{input_folder}'.")
        return

    for pdf_file in pdf_files:
        input_pdf_path = os.path.join(input_folder, pdf_file)
        output_pdf_path = os.path.join(output_folder, pdf_file)

        print(f"\n📄 Processing '{pdf_file}'...")
        process_pdf(input_pdf_path, output_pdf_path)


if __name__ == "__main__":
    # Folder paths
    input_folder = r"C:\CitiDev\pdfmyocr\input"
    output_folder = r"C:\CitiDev\pdfmyocr\output"

    process_all_pdfs(input_folder, output_folder)
