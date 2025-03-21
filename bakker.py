⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

df = parse_mrz(mrl1, mrl2)
print(df)

import cv2
import numpy as np
import pytesseract
import math

# Set Tesseract path if required
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_rotation_angle(image):
    """Detects the rotation angle using Tesseract OSD and Hough Transform."""
    # Step 1: Use Tesseract OSD for orientation detection
    osd = pytesseract.image_to_osd(image)
    angle_osd = int(osd.split("\n")[1].split(":")[-1].strip())

    # Step 2: Convert to grayscale and apply edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Step 3: Detect lines using Hough Transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = (theta * 180 / np.pi) - 90  # Convert radians to degrees
            if -45 < angle < 45:  # Filter relevant angles
                angles.append(angle)

    # Step 4: Compute final angle
    angle_hough = np.median(angles) if angles else 0
    final_angle = angle_osd if abs(angle_osd) > abs(angle_hough) else angle_hough

    return final_angle

def correct_rotation(image):
    """Corrects rotation based on detected angle."""
    angle = detect_rotation_angle(image)
    if abs(angle) > 0.5:  # Only rotate if angle is significant
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    return image

def deskew_pca(image):
    """Corrects skew using PCA (Principal Component Analysis)."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binary threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours
    coords = np.column_stack(np.where(binary > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # Fix angles returned by OpenCV
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Rotate image to deskew
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return deskewed

def preprocess_image(image_path, output_path="final_corrected.jpg"):
    """Loads image, applies advanced skew and rotation correction, and saves output."""
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

