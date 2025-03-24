⁸

import os
import cv2
import numpy as np
import aspose.ocr as ecr  # Aspose OCR for skew detection
import fitz  # PyMuPDF for handling PDFs
from PIL import Image

def correct_skew(image, angle):
    """Correct skew using OpenCV rotation based on the detected angle."""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected

# Initialize Aspose.OCR API
api = ecr.AsposeOCR()

# File path (Update this to your file location)
file_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\Skewed- Payment advice.pdf"

# Define output folder
output_folder = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Output"
os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist

# Detect if it's an image, TIFF, or PDF
if file_path.lower().endswith(".pdf"):
    input_type = ecr.InputType.PDF
elif file_path.lower().endswith((".tiff", ".tif", ".png", ".jpg", ".jpeg")):
    input_type = ecr.InputType.SINGLE_IMAGE
else:
    raise ValueError("Unsupported file format!")

# Processing for PDFs
if input_type == ecr.InputType.PDF:
    # Load the PDF
    pdf_document = fitz.open(file_path)
    corrected_images = []

    for page_number in range(len(pdf_document)):
        # Convert each page to an image
        pix = pdf_document[page_number].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert PIL image to OpenCV format
        image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Add image to OCR batch
        ocr_input = ecr.OcrInput(ecr.InputType.SINGLE_IMAGE)
        temp_image_path = os.path.join(output_folder, f"temp_page_{page_number + 1}.png")
        cv2.imwrite(temp_image_path, image)  # Save temp file for OCR
        ocr_input.add(temp_image_path)

        # Detect skew angle
        angles = api.calculate_skew(ocr_input)
        if angles:
            best_angle = angles[0].angle
            print(f"Page {page_number + 1} - Detected Skew Angle: {best_angle:.1f}°")

            # Correct skew
            corrected_image = correct_skew(image, best_angle)
            corrected_images.append(corrected_image)

            # Remove temporary image file
            os.remove(temp_image_path)
        else:
            print(f"Page {page_number + 1} - No skew detected.")
            corrected_images.append(image)

    # Save corrected images back to PDF
    output_pdf_path = os.path.join(output_folder, "corrected_output.pdf")
    corrected_pil_images = [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in corrected_images]
    corrected_pil_images[0].save(output_pdf_path, save_all=True, append_images=corrected_pil_images[1:])
    
    print("Final corrected PDF saved at:", output_pdf_path)

else:
    # Process single images (PNG, JPG, TIFF)
    ocr_input = ecr.OcrInput(ecr.InputType.SINGLE_IMAGE)
    ocr_input.add(file_path)
    angles = api.calculate_skew(ocr_input)

    if angles:
        best_angle = angles[0].angle
        print(f"Detected Skew Angle: {best_angle:.1f}°")

        # Load the image
        image = cv2.imread(file_path)

        if image is None:
            print("Error: Could not read image. Ensure the file path is correct.")
        else:
            corrected_image = correct_skew(image, best_angle)

            # Save the corrected image
            file_name = os.path.basename(file_path)
            save_path = os.path.join(output_folder, f"corrected_{file_name}")
            cv2.imwrite(save_path, corrected_image)

            print("Corrected image saved at:", save_path)

            cv2.imshow("Corrected Image", corrected_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("No skew detected.")

