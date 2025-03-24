import fitz  # PyMuPDF
import cv2
import numpy as np
import os
from scipy.ndimage import interpolation as inter
import aspose.ocr as ocr
from PIL import Image

# Instantiate Aspose.OCR API
api = ocr.AsposeOCR()

def correct_skew(image, angle):
    """ Rotates the image to correct skew """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected

def process_pdf(file_path, output_pdf_path):
    """ Processes multi-page PDF for skew detection and correction """
    pdf_document = fitz.open(file_path)
    output_images = []
    temp_image_path = r"C:\temp_skewed_image.jpg"  # Temporary image storage

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
        cv2.imwrite(temp_image_path, img)

        # Perform skew detection using AsposeOCR
        ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
        ocr_input.add(temp_image_path)  # Use the saved image file
        angles = api.calculate_skew(ocr_input)

        if angles:
            skew_angle = angles[0].angle  # Get skew angle for this page
            print(f"Page {page_num + 1}: Skew Angle Detected = {skew_angle:.2f}°")
            img = correct_skew(img, -skew_angle)  # Correct skew
        else:
            print(f"Page {page_num + 1}: No skew detected")

        # Convert OpenCV image back to PIL for PDF saving
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        output_images.append(img_pil)

    # Save all corrected pages as a new PDF
    output_images[0].save(output_pdf_path, save_all=True, append_images=output_images[1:])

    # Remove temporary image file
    os.remove(temp_image_path)

    print(f"\n✅ Skew-corrected PDF saved at: {output_pdf_path}")

def process_image(file_path, output_image_path):
    """ Processes a single image for skew detection and correction """
    print(f"Processing image: {file_path}")

    # Read image
    img = cv2.imread(file_path)
    
    if img is None:
        print("❌ Error: Unable to read the image file!")
        return

    # Perform skew detection using AsposeOCR
    ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
    ocr_input.add(file_path)
    angles = api.calculate_skew(ocr_input)

    if angles:
        skew_angle = angles[0].angle  # Get skew angle for this image
        print(f"Skew Angle Detected = {skew_angle:.2f}°")
        img = correct_skew(img, -skew_angle)  # Correct skew
    else:
        print("No skew detected")

    # Save corrected image
    cv2.imwrite(output_image_path, img)
    print(f"✅ Skew-corrected image saved at: {output_image_path}")

if __name__ == "__main__":
    # File paths
    file_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\Skewed- Payment advice.pdf"
    output_folder = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Output"

    # Determine if the input is a PDF or an image
    if file_path.lower().endswith(".pdf"):
        output_pdf_path = os.path.join(output_folder, "Corrected.pdf")
        process_pdf(file_path, output_pdf_path)
    else:
        output_image_path = os.path.join(output_folder, "Corrected.png")
        process_image(file_path, output_image_path)

