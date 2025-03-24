import os
import numpy as np
from PIL import Image
import pdf2image
import cv2
from pathlib import Path
import aspose.ocr as ocr


def process_document(file_path, output_dir):
    input_path = Path(file_path)
    output_file = output_dir / f"{input_path.stem}_processed.pdf"

    file_ext = input_path.suffix.lower()
    processed_images = []

    if file_ext == '.pdf':
        images = pdf2image.convert_from_path(file_path, dpi=300)
        if not images:
            raise ValueError(f"Failed to extract images from {file_path}")

        for img in images:
            img = process_image(img)
            processed_images.append(img)

        save_as_pdf(processed_images, output_file)
        print(f"Processed: {file_path} -> {output_file}")


def save_as_pdf(images, output_path):
    images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)


def correct_skew(image, angle):
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
    input_folder = Path(r"\\apachkwinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\skewedpdf")
    output_folder = Path(r"C:\CitiDev\pdfmyocr\output")

    # Ensure output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)

    # Process all PDFs in input folder
    for pdf_file in input_folder.glob("*.pdf"):
        process_document(pdf_file, output_folder)


if __name__ == "__main__":
    main()
