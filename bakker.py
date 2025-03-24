⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = 


import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_for_osd(image):
    """Ensure image is grayscale and resized for better OSD detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Resize small images to at least 1000px width for better text recognition
    height, width = gray.shape[:2]
    if width < 1000:
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
            if -45 < angle < 45:  # Consider valid angles
                angles.append(angle)

    return np.median(angles) if angles else 0

def detect_rotation_angle(image):
    """Detects rotation angle while handling flipped images correctly."""
    gray = preprocess_for_osd(image)

    try:
        osd = pytesseract.image_to_osd(gray)
        angle_osd = int(osd.split("\n")[1].split(":")[-1].strip())
    except pytesseract.TesseractError:
        print("⚠ Tesseract OSD failed. Using Hough Transform as backup.")
        return detect_hough_angle(image)

    # Fix incorrect 180° misreads
    if angle_osd == 180:
        print("🔄 Image is upside down! Fixing...")
        image = cv2.rotate(image, cv2.ROTATE_180)
        return 0  # No need for further correction

    return angle_osd

def correct_rotation(image):
    """Corrects rotation based on detected angle."""
    angle = detect_rotation_angle(image)

    if abs(angle) > 0.5:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        print(f"✅ Corrected Rotation Angle: {-angle:.2f}°")
        return rotated

    return image  # Return original if no rotation needed

def deskew_pca(image):
    """Corrects skew using PCA (Principal Component Analysis)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    coords = np.column_stack(np.where(binary > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    print(f"✅ Corrected Skew Angle: {-angle:.2f}°")
    return deskewed

def check_mirrored(image):
    """Detects if an image is mirrored (flipped left-right) and fixes it."""
    flipped = cv2.flip(image, 1)
    text_orig = pytesseract.image_to_string(image).strip()
    text_flipped = pytesseract.image_to_string(flipped).strip()

    if len(text_flipped) > len(text_orig):
        print("🔄 Detected mirrored (reversed) image! Fixing...")
        return flipped
    return image

def preprocess_image(image_path, output_path="final_corrected.jpg"):
    """Loads image, applies advanced corrections, and saves the final output."""
    print("\n🔍 Processing Image:", image_path)
    image = cv2.imread(image_path)

    # Step 1: Check if image is mirrored and correct it
    image = check_mirrored(image)

    # Step 2: Deskew using PCA
    image = deskew_pca(image)

    # Step 3: Correct Rotation
    image = correct_rotation(image)

    cv2.imwrite(output_path, image)
    print(f"📂 Final corrected image saved as: {output_path}\n")
    return image

# Example Usage
preprocess_image("reversed_skewed_rotated_text.jpg", "final_corrected_text.jpg")
