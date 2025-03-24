⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 

import cv2
import numpy as np
import pytesseract
import re

# Set Tesseract path (for Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_rotation_angle(image):
    """Detects the rotation angle using Tesseract OSD and Hough Transform."""
    
    # Step 1: Use Tesseract OSD to detect orientation
    osd_data = pytesseract.image_to_osd(image)
    angle_match = re.search(r"Rotate: (\d+)", osd_data)
    angle_osd = int(angle_match.group(1)) if angle_match else 0

    # Convert 180 and 270 degrees to negative angles for better rotation
    if angle_osd == 180:
        angle_osd = -180
    elif angle_osd == 270:
        angle_osd = -90

    # Step 2: Convert image to grayscale and detect edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Step 3: Detect lines using Hough Transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angles = []

    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = (theta * 180 / np.pi) - 90  # Convert radians to degrees
            if -45 < angle < 45:  # Filter only relevant angles
                angles.append(angle)

    # Compute the final angle based on median of detected angles
    angle_hough = np.median(angles) if angles else 0

    # Choose the best angle from Tesseract OSD or Hough Transform
    final_angle = angle_osd if abs(angle_osd) > abs(angle_hough) else angle_hough

    return final_angle

def correct_rotation(image):
    """Corrects rotation based on detected angle."""
    angle = detect_rotation_angle(image)
    if abs(angle) > 0.5:  # Rotate only if angle is significant
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    return image

def deskew_pca(image):
    """Corrects skew using PCA (Principal Component Analysis)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binary threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find text contours and compute the skew angle
    coords = np.column_stack(np.where(binary > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # Adjust skew angle based on OpenCV's output
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Apply rotation correction for skew
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return deskewed

def preprocess_image(image_path, output_path="final_corrected.jpg"):
    """Loads image, applies skew and rotation correction, and saves output."""
    image = cv2.imread(image_path)

    # Step 1: Deskew using PCA
    image = deskew_pca(image)

    # Step 2: Correct Rotation using OSD + Hough Lines
    image = correct_rotation(image)

    # Save the corrected image
    cv2.imwrite(output_path, image)
    return image

# Example Usage
preprocess_image("skewed_rotated_text.jpg", "final_corrected_text.jpg")
