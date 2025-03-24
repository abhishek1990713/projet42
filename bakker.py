⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 


import cv2
import numpy as np
import pytesseract
import math

# Set Tesseract path if required
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_rotation_angle(image):
    """Detects the rotation angle using Tesseract OSD and Hough Transform."""
    
    # Ensure image is valid
    if image is None:
        print("Error: Image not loaded properly!")
        return 0

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to enhance text
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 31, 2)

    # Save as temporary image to fix DPI issue
    temp_path = "temp_fixed_dpi.png"
    cv2.imwrite(temp_path, thresh, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    # Try running Tesseract OSD
    try:
        osd = pytesseract.image_to_osd(temp_path)
        angle_osd = int(osd.split("\n")[1].split(":")[-1].strip())
    except pytesseract.TesseractError as e:
        print("Tesseract OSD failed:", e)
        return 0  # Default to no rotation if OSD fails

    return angle_osd

def correct_rotation(image):
    """Corrects rotation based on detected angle without flipping 180 degrees."""
    
    angle = detect_rotation_angle(image)
    
    if abs(angle) > 0.5:  # Only rotate if angle is significant
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)

        # Ensure angle is within -90 to 90 degrees
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    return image

def deskew_pca(image):
    """Corrects skew using PCA (Principal Component Analysis)."""
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binary threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find coordinates of non-zero pixels
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

    # Load the image
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return None

    print(f"Processing Image: {image_path}")

    # Step 1: Deskew using PCA
    image = deskew_pca(image)

    # Step 2: Correct Rotation using OSD
    image = correct_rotation(image)

    # Save the corrected image
    cv2.imwrite(output_path, image)
    print(f"Final corrected image saved as: {output_path}")

    return image

# Example Usage
preprocess_image(r"C:\CitiDev\pdfmyocr\input\Skewed- Payment advice.png", r"C:\CitiDev\pdfmyocr\metric12.jpg")
