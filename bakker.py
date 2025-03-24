⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

import cv2
import numpy as np
import pytesseract

# Set Tesseract path if required
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_for_osd(image):
    """Preprocess image for better Tesseract OSD detection (grayscale + resize)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Ensure the image has high enough resolution for OCR (Resize if needed)
    height, width = gray.shape[:2]
    if width < 1000:  # Scale up small images for better text detection
        scale_factor = 1000 / width
        gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    return gray

def detect_hough_angle(image):
    """Fallback method: Detect rotation using Hough Transform."""
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
    print(f"📌 Fallback Hough Rotation Angle: {angle_hough:.2f}°")
    return angle_hough

def detect_rotation_angle(image):
    """Detect rotation angle with fallback if OSD fails."""
    gray = preprocess_for_osd(image)

    try:
        osd = pytesseract.image_to_osd(gray)
        angle_osd = int(osd.split("\n")[1].split(":")[-1].strip())
    except pytesseract.TesseractError:
        print("⚠ Tesseract OSD failed. Using Hough Transform as backup.")
        return detect_hough_angle(image)

    print(f"📌 Detected Rotation Angle: {angle_osd:.2f}°")
    return angle_osd

def correct_rotation(image):
    """Corrects rotation based on detected angle while avoiding unnecessary 180° flips."""
    angle = detect_rotation_angle(image)

    # Prevent unnecessary 180° flipping
    if abs(angle) == 180:
        print(f"⚠ Skipping 180° rotation to avoid flipping the image.")
        return image

    if abs(angle) > 0.5:  # Only rotate if angle is significant
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        print(f"✅ Corrected Rotation Angle: {-angle:.2f}°")
        return rotated

    print("✅ No significant rotation detected.")
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

    print(f"📌 Detected Skew Angle: {angle:.2f}°")  # Print detected skew angle

    # Rotate image to deskew
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    print(f"✅ Corrected Skew Angle: {-angle:.2f}°")  # Print correction
    return deskewed

def preprocess_image(image_path, output_path="final_corrected.jpg"):
    """Loads image, applies advanced skew and rotation correction, and saves output."""
    print("\n🔍 Processing Image:", image_path)

    image = cv2.imread(image_path)

    # Step 1: Deskew using PCA
    image = deskew_pca(image)

    # Step 2: Correct Rotation using OSD + Hough Lines
    image = correct_rotation(image)

    # Save the corrected image
    cv2.imwrite(output_path, image)
    print(f"📂 Final corrected image saved as: {output_path}\n")
    return image

# Example Usage
preprocess_image("skewed_rotated_text.jpg", "final_corrected_text.jpg")
