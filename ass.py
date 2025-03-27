

import fitz  # PyMuPDF for direct PDF handling
import os
import cv2
import numpy as np
from PIL import Image


def correct_skew(file_path, angles, output_path):
    """Correct skew fo

    import os
import numpy as np
from PIL import Image, ImageSequence
import pdf2image
import cv2
from pathlib import Path
import aspose.ocr as ocr

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_file(file_path, output_folder):
    """
    Processes a single PDF or image file and saves the output in the given folder.
    
    - PDFs → Outputs a processed PDF
    - Images (JPG, PNG, TIF, etc.) → Outputs a processed TIFF file
    """
    input_path = Path(file_path)
    file_ext = input_path.suffix.lower()
    output_path = Path(output_folder) / input_path.name  # Keep the same name

    if file_ext == ".pdf":
        process_pdf(file_path, output_path.with_suffix(".pdf"))
    elif file_ext in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]:
        process_image_file(file_path, output_path.with_suffix(".tiff"))
    else:
        print(f"Unsupported file format: {file_ext}")

def process_pdf(pdf_path, output_pdf):
    """Extracts images from a PDF, applies skew correction, and saves as a processed PDF."""
    images = pdf2image.convert_from_path(pdf_path)

    if not images:
        raise ValueError(f"Failed to extract images from {pdf_path}")

    processed_images = [process_image(img) for img in images]

    save_as_pdf(processed_images, output_pdf)

    print(f"Processed PDF: {pdf_path} -> {output_pdf}")

def process_image_file(image_path, output_path):
    """Processes a single image file or multipage TIFF, applies skew correction, and saves as TIFF."""
    image = Image.open(image_path)

    if image.format == 'TIFF' and hasattr(image, 'n_frames') and image.n_frames > 1:
        processed_images = []
        for i, page in enumerate(ImageSequence.Iterator(image)):
            processed_image = process_image(page)
            processed_images.append(processed_image)

        processed_images[0].save(output_path, save_all=True, append_images=processed_images[1:], resolution=100.0, compression="tiff_lzw")
    else:
        processed_image = process_image(image)
        processed_image.save(output_path, format="TIFF")

    print(f"Processed Image: {image_path} -> {output_path}")

def process_image(image):
    """Applies OCR-based skew correction to an image."""
    api = ocr.AsposeOcr()
    ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)

    temp_image_path = "temp_image.png"
    image.save(temp_image_path)
    ocr_input.add(temp_image_path)

    angles = api.calculate_skew(ocr_input)
    img = cv2.imread(temp_image_path)

    if angles and img is not None:
        skew_angle = angles[0].angle  # Get detected skew angle
        print(f"Skew Angle Detected: {skew_angle:.2f}°")
        img = correct_skew(img, skew_angle)
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # Convert back to PIL Image
    else:
        print("No skew detected.")
        img = image

    return img

def correct_skew(image, angle):
    """Corrects skew in an image using OpenCV rotation."""
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

def save_as_pdf(images, output_path):
    """Saves a list of PIL images as a PDF."""
    images[0].save(output_path, save_all=True, append_images=images[1:])

def main():
    """Processes all files in the input folder and saves them in the output folder."""
    input_folder = Path(INPUT_FOLDER)
    output_folder = Path(OUTPUT_FOLDER)

    if not input_folder.exists():
        print(f"Error: Input folder '{INPUT_FOLDER}' does not exist!")
        return

    files = list(input_folder.glob("*.*"))  # Get all files

    if not files:
        print("No files found in the input folder.")
        return

    for file in files:
        process_file(file, output_folder)

if __name__ == "__main__":
    main()
