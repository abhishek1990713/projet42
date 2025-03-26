

import os
import numpy as np
from PIL import Image
import pdf2image
import cv2
from pathlib import Path
import aspose.ocr as ocr


def process_document(file_path, output_dir):
    """Process a single PDF document, extract images, correct skew, and save as new PDF."""
    file_name = Path(file_path).stem  # Get PDF name without extension
    output_pdf_path = os.path.join(output_dir, f"{file_name}_processed.pdf")

    images = pdf2image.convert_from_path(file_path, dpi=300)
    if not images:
        raise ValueError(f"Failed to extract images from PDF: {file_path}")

    processed_images = [process_image(img) for img in images]

    # Save processed images as a new PDF
    save_as_pdf(processed_images, output_pdf_path)

    print(f"Processed and saved: {output_pdf_path}")
    return output_pdf_path


def save_as_pdf(images, output_path):
    """Save a list of images as a PDF."""
    images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)


def correct_skew(image, angle):
    """Correct the skew in an image using the detected angle."""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    abs_cos = abs(np.cos(np.radians(angle)))
    abs_sin = abs(np.sin(np.radians(angle)))

    bound_w = int(h * abs_sin + w * abs_cos)
    bound_h = int(h * abs_cos + w * abs_sin)

    M = cv2.getRotationMatrix2D(center, angle, 1)
    M[0, 2] += (bound_w / 2) - center[0]
    M[1, 2] += (bound_h / 2) - center[1]

    corrected = cv2.warpAffine(image, M, (bound_w, bound_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected


def process_image(image):
    """Perform OCR-based skew correction on an image."""
    api = ocr.AsposeOcr()
    ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)

    image_path = "temp_image.png"
    image.save(image_path)

    ocr_input.add(image_path)
    angles = api.calculate_skew(ocr_input)

    img = cv2.imread(image_path)

    if angles and img is not None:
        skew_angle = angles[0].angle  # Get skew angle
        print(f"{image_path}: Skew Angle Detected = {skew_angle:.2f}")
        img = correct_skew(img, skew_angle)  # Correct skew
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # Convert back to PIL Image
    else:
        print(f"{image_path}: No skew detected")
        img = image

    return img


def main():
    """Process all PDF files in the input folder and save outputs in the output folder."""
    input_folder = r"\\apachkwinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\skewedpdf"
    output_folder = r"C:\CitiDev\pdfmyocr\output"

    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in the input folder.")
        return

    for pdf_file in pdf_files:
        input_pdf_path = os.path.join(input_folder, pdf_file)
        try:
            process_document(input_pdf_path, output_folder)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")


if __name__ == "__main__":
    main()
