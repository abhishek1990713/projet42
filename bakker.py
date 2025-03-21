⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

df = parse_mrz(mrl1, mrl2)
print(df)


import cv2
import numpy as np

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
    """Loads image, applies skew correction only, and saves output."""
    print("\n🔍 Processing Image:", image_path)

    image = cv2.imread(image_path)

    # Correct skew
    image = deskew_pca(image)

    # Save the corrected image
    cv2.imwrite(output_path, image)
    print(f"📂 Final corrected image saved as: {output_path}\n")
    return image

# Example Usage
preprocess_image("skewed_text.jpg", "final_corrected_text.jpg")
