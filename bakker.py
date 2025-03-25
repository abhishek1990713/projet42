import os
import numpy as np
from PIL import Image
import pdf2image
import cv2
from pathlib import Path
import aspose.ocr as ocr
from io import BytesIO


def process_file(file_path):
    """
    Processes a single PDF or image file.
    - PDFs → Outputs a processed PDF
    - Images (JPG, PNG, TIF, etc.) → Outputs a processed image in the same format
    """
    input_path = Path(file_path)
    file_ext = input_path.suffix.lower()

    output_path = input_path.parent / f"{input_path.stem}_processed{file_ext}"

    if file_ext == ".pdf":
        process_pdf(file_path, output_path)
    elif file_ext in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]:
        process_image_file(file_path, output_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

    return str(output_path)


def process_pdf(pdf_path, output_pdf):
    """Extracts images from a PDF, applies skew correction, and saves as a processed PDF."""
    images = pdf2image.convert_from_path(pdf_path, dpi=300)

    if not images:
        raise ValueError(f"Failed to extract images from {pdf_path}")

    processed_images = [process_image(img) for img in images]
    
    save_as_pdf(processed_images, output_pdf)
    print(f"Processed PDF saved at: {output_pdf}")


def process_image_file(image_path, output_image):
    """Processes a single image file, applies skew correction, and saves it back in the same format."""
    image = Image.open(image_path)
    processed_image = process_image(image)
    processed_image.save(output_image)
    print(f"Processed Image saved at: {output_image}")


def process_image(image):
    """Processes an image in memory, applies skew correction using OCR, and returns the processed image."""
    api = ocr.AsposeOcr()
    ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)

    # Convert image to bytes (in-memory)
    image_bytes = BytesIO()
    image.save(image_bytes, format="PNG")  # Keeping it in PNG format for OCR processing
    image_data = image_bytes.getvalue()

    # Perform OCR-based skew detection
    ocr_input.add_binary(image_data, "image.png")  # Pass image data directly without saving a file
    angles = api.calculate_skew(ocr_input)

    # Convert PIL image to OpenCV format (NumPy array)
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    if angles:
        skew_angle = angles[0].angle  # Get detected skew angle
        print(f"Skew Angle Detected: {skew_angle:.2f}°")
        img = correct_skew(img, skew_angle)  # Correct skew

        # Convert back to PIL Image
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
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


# Example Usage
if __name__ == "__main__":
    file_path = input("Enter the file path: ").strip()
    output_file = process_file(file_path)
    print(f"Processing completed. Output saved at: {output_file}")
