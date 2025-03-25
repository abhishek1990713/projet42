import os
import numpy as np
from PIL import Image
import pdf2image
import cv2
from pathlib import Path

def process_document(file_path, output_dir=None):
    """
    Processes a document (PDF, PNG, TIFF) and saves the corrected output in the same format.
    """
    input_path = Path(file_path)
    
    if output_dir is None:
        output_dir = input_path.parent / f"{input_path.stem}_processed"
    
    os.makedirs(output_dir, exist_ok=True)

    file_ext = input_path.suffix.lower()
    
    if file_ext in ['.png', '.tiff', '.tif']:
        # Process single image
        img = Image.open(file_path)
        processed_img = process_image(img)

        output_path = os.path.join(output_dir, f"{input_path.stem}_processed{file_ext}")
        processed_img.save(output_path)

    elif file_ext == '.pdf':
        # Process multiple pages in a PDF
        images = pdf2image.convert_from_path(file_path, dpi=300)
        if not images:
            raise ValueError("Failed to extract images from PDF")

        processed_images = [process_image(img) for img in images]

        output_path = os.path.join(output_dir, f"{input_path.stem}_processed.pdf")
        save_as_pdf(processed_images, output_path)
    
    else:
        raise ValueError("Unsupported file format. Only PNG, TIFF, and PDF are allowed.")

    print(f"Processed file saved at: {output_path}")
    return output_path


def save_as_pdf(images, output_path):
    """Saves multiple processed images as a PDF."""
    images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)


def correct_skew(image, angle):
    """Corrects skew in an image using the detected angle."""
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


def detect_skew_opencv(image):
    """Uses OpenCV to detect and correct skew without saving a temporary file."""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            angles.append(angle)

        skew_angle = np.median(angles)
        return correct_skew(image, skew_angle)  # Correct skew
    return image


def process_image(pil_image):
    """Applies OpenCV-based skew detection and correction without saving temp files."""
    img = np.array(pil_image)  # Convert PIL to NumPy array (OpenCV format)
    img = detect_skew_opencv(img)  # Use OpenCV for skew detection and correction
    img = Image.fromarray(img)  # Convert back to PIL Image

    return img


def main():
    input_file = r"\\apachkwinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\skewedpdf\@@@@@@@2661910562039_FBM"
    output_folder = r"C:\CitiDev\pdfmyocr\output"

    process_document(input_file, output_folder)


if __name__ == "__main__":
    main()
