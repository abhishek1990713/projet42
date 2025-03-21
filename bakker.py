⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

df = parse_mrz(mrl1, mrl2)
print(df)


import cv2
import numpy as np
import cv2
import numpy as np
import pytesseract

# Set Tesseract path if required
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_rotation_angle(image):
    """Detects rotation angle using Tesseract OSD & Hough Line Transform."""
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

    # Step 4: Compute final angle (selecting the most reliable one)
    angle_hough = np.median(angles) if angles else 0
    final_angle = angle_osd if abs(angle_osd) > abs(angle_hough) else angle_hough

    print(f"📌 Detected Rotation Angle: {final_angle:.2f}°")  # Print detected angle
    return final_angle

def correct_rotation(image):
    """Corrects rotation based on detected angle and prints updated angle."""
    angle = detect_rotation_angle(image)
    
    if abs(angle) > 0.5:  # Only rotate if angle is significant
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        print(f"✅ Corrected Rotation Angle: {-angle:.2f}°")  # Print correction
        return rotated

    print("✅ No significant rotation detected.")
    return image

def deskew_pca(image):
    """Corrects skew using Principal Component Analysis (PCA) and prints the skew angle."""
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
