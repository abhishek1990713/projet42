

import cv2
import os
import aspose.ocr as ocr

# Instantiate Aspose.OCR API
api = ocr.AsposeOCR()

def detect_skew_angle(image_path):
    """Detects the skew angle of a given image."""
    if not os.path.exists(image_path):
        print(f"X Error: File '{image_path}' not found.")
        return

    print(f"Processing image: {image_path}")

    img = cv2.imread(image_path)

    if img is None:
        print("X Error: Unable to read the image file.")
        return

    # Perform skew detection using AsposeOCR
    try:
        ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
        ocr_input.add(image_path)
        angles = api.calculate_skew(ocr_input)
    except RuntimeError as e:
        print(f"A Warning: Skew detection failed - {e}")
        return

    if angles:
        skew_angle = angles[0].angle
        print(f"Skew Angle Detected = {skew_angle:.2f}")
        return skew_angle
    else:
        print("No skew detected")
        return None

if __name__ == "__main__":
    # Example: Replace with your actual image path
    image_path = r"your_image_path_here.jpg"  # Provide the path to your image

    detected_angle = detect_skew_angle(image_path)

    if detected_angle is not None:
        print(f"Detected skew angle: {detected_angle:.2f}°")
    else:
        print("No skew angle detected.")
