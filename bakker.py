import os
import numpy as np
from PIL import Image
import pdf2image
import cv2
from pathlib import Path
import aspose.ocr as ocr


def process_file(file_path):
    """
    Processes a single PDF or image file.
    - PDFs → Outputs a processed PDF
    - Images (JPG, PNG, TIF, etc.) → Outputs a processed TIFF file
    """
    input_path = Path(file_path)
    file_ext = input_path.suffix.lower()
    output_path = input_path.with_stem(input_path.stem + "_processed")

    if file_ext == ".pdf":
        process_pdf(file_path, output_path.with_suffix(".pdf"))
    elif file_ext in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]:
        process_image_file(file_path, output_path.with_suffix(".tiff"))
    else:
        print(f"Unsupported file format: {file_ext}")


def process_pdf(pdf_path, output_pdf):
    """Extracts images from a PDF, applies skew correction, and saves as a processed PDF."""
    images = pdf2image.convert_from_path(pdf_path, dpi=300)
    
    if not images:
        raise ValueError(f"Failed to extract images from {pdf_path}")

    processed_images = [process_image(img) for img in images]
    
    save_as_pdf(processed_images, output_pdf)
    print(f"Processed PDF: {pdf_path} -> {output_pdf}")


def process_image_file(image_path, output_tiff):
    """Processes a single image file, applies skew correction, and saves as TIFF."""
    image = Image.open(image_path)
    processed_image = process_image(image)
    processed_image.save(output_tiff, format="TIFF")
    print(f"Processed Image: {image_path} -> {output_tiff}")


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
    images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)


def main():
    file_path = input("Enter the full path of the PDF or image: ").strip()

    if not os.path.exists(file_path):
        print("Error: File does not exist!")
        return

    process_file(file_path)


if __name__ == "__main__":
    main()

