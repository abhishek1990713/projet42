⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

import cv2
import numpy as np
import pytesseract
import os
from PIL import Image

# Set Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Define input & output folders
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_tiff_to_png(image_path):
    """Converts TIFF to PNG for better OCR processing."""
    img = Image.open(image_path)
    png_path = image_path.replace(".tiff", ".png")
    img.save(png_path, format="PNG")
    return png_path

def force_minimum_dpi(image_path):
    """Ensures image has a minimum DPI of 150 to avoid Tesseract errors."""
    img = Image.open(image_path)
    img.save(image_path, dpi=(150, 150))

def detect_rotation_angle(image):
    """Detects rotation using Tesseract OSD with fallback to 0°."""
    h, w = image.shape[:2]
    if h < 500 or w < 500:  # Resize small images for better OCR
        scale = 2.0
        image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)  # Improve contrast

    try:
        osd = pytesseract.image_to_osd(gray)
        angle_osd = int(osd.split("\n")[1].split(":")[-1].strip())
        print(f"📌 Detected Rotation Angle: {angle_osd:.2f}°")
        return angle_osd
    except pytesseract.TesseractError:
        print("⚠ No text detected, skipping rotation correction.")
        return 0  # Default to 0° if OCR fails

def correct_rotation(image):
    """Corrects rotation based on detected angle while preventing unnecessary 180° flips."""
    angle = detect_rotation_angle(image)

    if abs(angle) == 180:
        print(f"⚠ Skipping 180° rotation to avoid flipping.")
        return image

    if abs(angle) > 0.5:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        print(f"✅ Corrected Rotation Angle: {-angle:.2f}°")
        return rotated

    print("✅ No significant rotation detected.")
    return image

def deskew_pca(image):
    """Corrects skew using PCA-based angle detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    coords = np.column_stack(np.where(binary > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    print(f"📌 Detected Skew Angle: {angle:.2f}°")

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    print(f"✅ Corrected Skew Angle: {-angle:.2f}°")
    return deskewed

def preprocess_images():
    """Processes all images from input folder and saves corrected images to output folder."""
    print(f"\n🔍 Processing images from folder: {INPUT_FOLDER}\n")

    image_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff'))]

    if not image_files:
        print("❌ No images found in input folder.")
        return

    for img_name in image_files:
        input_path = os.path.join(INPUT_FOLDER, img_name)
        output_path = os.path.join(OUTPUT_FOLDER, img_name)

        print(f"📂 Processing: {img_name}")

        # Convert TIFF to PNG if needed
        if input_path.lower().endswith(".tiff"):
            input_path = convert_tiff_to_png(input_path)

        # Force minimum DPI
        force_minimum_dpi(input_path)

        # Read image
        image = cv2.imread(input_path)

        # Step 1: Deskew
        image = deskew_pca(image)

        # Step 2: Correct Rotation
        image = correct_rotation(image)

        # Save corrected image
        cv2.imwrite(output_path, image)
        print(f"✅ Saved corrected image: {output_path}\n")

# Run preprocessing
preprocess_images()
