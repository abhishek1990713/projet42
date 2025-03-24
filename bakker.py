import fitz  # PyMuPDF
import cv2
import numpy as np
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

# File path
file_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\Skewed- Payment advice.pdf"

# Open PDF
pdf_document = fitz.open(file_path)
output_images = []

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

    # Perform skew detection using AsposeOCR
    ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
    ocr_input.add_image_from_bytes(img.tobytes(), pix.w, pix.h, ocr.ImageType.JPG)
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
output_pdf_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Output\Corrected.pdf"
output_images[0].save(output_pdf_path, save_all=True, append_images=output_images[1:])

print(f"\n✅ Skew-corrected PDF saved at: {output_pdf_path}")

