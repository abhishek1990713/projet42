⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"


import cv2
import numpy as np
import pytesseract
import re

# Set Tesseract path (for Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def increase_dpi(image, dpi=300):
    """Increases image DPI to improve OCR performance."""
    height, width = image.shape[:2]
    scale_factor = dpi / 70  # Scale relative to Tesseract's default 70 DPI
    new_size = (int(width * scale_factor), int(height * scale_factor))
    high_res_image = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)
    return high_res_image

def find_rotation_angle(image_path):
    """Finds the rotation angle of an image using Tesseract OSD and Hough Transform."""
    
    # Load the image
    image = cv2.imread(image_path)
    
    # Check if the image was loaded correctly
    if image is None:
        raise ValueError(f"Error: Could not load image at {image_path}. Please check the file path.")

    # Convert to grayscale (improves OCR performance)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Ensure image resolution is at least 300 DPI
    if gray.shape[1] < 500 or gray.shape[0] < 500:
        print("Low-resolution image detected. Increasing DPI...")
        gray = increase_dpi(gray)

    # Step 1: Use Tesseract OSD for orientation detection
    try:
        osd_data = pytesseract.image_to_osd(gray)
        angle_match = re.search(r"Rotate: (\d+)", osd_data)
        angle_osd = int(angle_match.group(1)) if angle_match else 0

        # Convert 180 and 270 degrees to negative angles for better rotation
        if angle_osd == 180:
            angle_osd = -180
        elif angle_osd == 270:
            angle_osd = -90

    except pytesseract.TesseractError as e:
        print("Tesseract OSD failed. Falling back to Hough Transform.")
        angle_osd = 0  # If Tesseract fails, use Hough Transform only

    # Step 2: Detect edges using Canny
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Step 3: Detect lines using Hough Transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angles = []

    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = (theta * 180 / np.pi) - 90  # Convert radians to degrees
            if -45 < angle < 45:  # Filter relevant angles
                angles.append(angle)

    # Compute the final angle based on median of detected angles
    angle_hough = np.median(angles) if angles else 0

    # Choose the best angle from Tesseract OSD or Hough Transform
    final_angle = angle_osd if abs(angle_osd) > abs(angle_hough) else angle_hough

    return final_angle

# Example Usage
image_path = "skewed_rotated_text.jpg"
angle = find_rotation_angle(image_path)
print(f"Detected Rotation Angle: {angle} degrees")
