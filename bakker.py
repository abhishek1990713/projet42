import os
import numpy as np
from PIL import Image
import pdf2image
import cv2
from pathlib import Path
import aspose.ocr as ocr  # ✅ Add AsposeOCR

def process_document(file_path, output_dir=None):
    input_path = Path(file_path)
    if output_dir is None:
        output_dir = input_path.parent / f"{input_path.stem}_processed"
    
    os.makedirs(output_dir, exist_ok=True)
    file_ext = input_path.suffix.lower()
    
    if file_ext in ['.png', '.tiff', '.tif']:
        img = Image.open(file_path)
        processed_img = process_image(img)

        output_path = os.path.join(output_dir, f"{input_path.stem}_processed{file_ext}")
        processed_img.save(output_path)

    elif file_ext == '.pdf':
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


def detect_skew_aspose(image):
    """Uses AsposeOCR to detect and correct skew."""
    api = ocr.AsposeOcr()
    ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)

    # ✅ Convert OpenCV image to AsposeOCR compatible format
    h, w = image.shape[:2]
    aspose_image = ocr.OcrImage(image, w, h)  # ✅ Use OcrImage instead of byte array

    ocr_input.add(aspose_image)  # ✅ Add image to OCR input
    angles = api.calculate_skew(ocr_input)

    if angles:
        skew_angle = angles[0].angle  # Get skew angle
        return correct_skew(image, skew_angle)
    
    return image  # No skew detected


def process_image(pil_image):
    """Uses AsposeOCR for skew detection & correction."""
    img = np.array(pil_image)  # Convert PIL to NumPy array (OpenCV format)
    img = detect_skew_aspose(img)  # ✅ Use AsposeOCR to detect skew
    img = Image.fromarray(img)  # Convert back to PIL Image

    return img


def main():
    input_file = r"\\apachkwinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\skewedpdf\@@@@@@@2661910562039_FBM"
    output_folder = r"C:\CitiDev\pdfmyocr\output"

    process_document(input_file, output_folder)


if __name__ == "__main__":
    main()

