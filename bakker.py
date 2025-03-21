⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

df = parse_mrz(mrl1, mrl2)
print(df)


import cv2
import numpy as np
import pytesseract
from PIL import Image

# Set Tesseract path if required (for Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def increase_dpi(image_path, output_path="high_dpi.png", dpi=300):
    """Increases image DPI for better OCR performance."""
    image = Image.open(image_path)
    image.save(output_path, dpi=(dpi, dpi))
    return output_path

def binarize_image(image):
    """Applies adaptive thresholding to clean up the text."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 2)
    return binary

def detect_skew_angle(image):
    """Detects the skew angle using PCA (Principal Component Analysis)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    coords = np.column_stack(np.where(binary > 0))
    angle = cv2.minAreaRect(coords)[-1]

    # Fix angles returned by OpenCV
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    return angle

def correct_skew(image):
    """Applies skew correction based on the detected angle."""
    angle = detect_skew_angle(image)
    if abs(angle) > 0.5:  # Only correct significant skew
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return image

def detect_rotation_angle(image):
    """Detects rotation angle using OpenCV Hough Transform and Tesseract OSD."""
    try:
        osd = pytesseract.image_to_osd(image, config="--psm 6")
        angle_osd = int(osd.split("\n")[1].split(":")[-1].strip())  # Extract angle from OSD
    except:
        angle_osd = 0  # If Tesseract fails, fallback to OpenCV

    # Hough Transform for backup detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = (theta * 180 / np.pi) - 90
            if -45 < angle < 45:
                angles.append(angle)

    angle_hough = np.median(angles) if angles else 0

    # Choose the most confident angle
    final_angle = angle_osd if abs(angle_osd) > abs(angle_hough) else angle_hough
    return final_angle

def correct_rotation(image):
    """Corrects rotation based on detected angle."""
    angle = detect_rotation_angle(image)
    if abs(angle) > 0.5:  # Only correct if the rotation is significant
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return image

def preprocess_image(image_path, output_path="final_corrected.jpg"):
    """Pipeline: Increase DPI → Binarization → Skew Correction → Rotation Correction."""
    image_path = increase_dpi(image_path)  # Increase DPI
    image = cv2.imread(image_path)

    image = binarize_image(image)  # Binarization
    image = correct_skew(image)  # Correct Skew
    image = correct_rotation(image)  # Correct Rotation

    cv2.imwrite(output_path, image)
    return image

# Example Usage
preprocess_image("Skewed- Payment advice.png", "final_corrected_text.jpg")

