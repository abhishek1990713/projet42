
import os
import cv2
import numpy as np
import pdf2image
from PIL import Image


def correct_skew(pdf_path, angle, output_path):
    """Correct the skew of a PDF using the given angle and save the corrected PDF."""
    print(f"\n🔄 Correcting skew for: {pdf_path} (Angle: {angle:.2f}°)")

    images = pdf2image.convert_from_path(pdf_path, dpi=300)

    if not images:
        print("❌ Failed to extract images from PDF.")
        raise ValueError(f"Failed to extract images from PDF: {pdf_path}")

    corrected_images = []

    for idx, img in enumerate(images):
        print(f"🔹 Processing page {idx + 1}/{len(images)}...")

        # Convert PIL Image to OpenCV format
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Correct the skew
        corrected_img_cv = rotate_image(img_cv, angle)

        # Convert back to PIL Image
        corrected_img = Image.fromarray(cv2.cvtColor(corrected_img_cv, cv2.COLOR_BGR2RGB))
        corrected_images.append(corrected_img)

    # Save as a new PDF
    save_as_pdf(corrected_images, output_path)
    print(f"✅ Corrected PDF saved: {output_path}")


def rotate_image(image, angle):
    """Rotate an image by the given angle to correct skew."""
    print(f"  ↪ Rotating image by {angle:.2f}°")

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    abs_cos = abs(np.cos(np.radians(angle)))
    abs_sin = abs(np.sin(np.radians(angle)))

    bound_w = int(h * abs_sin + w * abs_cos)
    bound_h = int(h * abs_cos + w * abs_sin)

    M = cv2.getRotationMatrix2D(center, angle, 1)
    M[0, 2] += (bound_w / 2) - center[0]
    M[1, 2] += (bound_h / 2) - center[1]

    rotated = cv2.warpAffine(image, M, (bound_w, bound_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def save_as_pdf(images, output_path):
    """Save a list of images as a PDF."""
    images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)
