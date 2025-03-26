
import os
import cv2
import numpy as np
import pdf2image
from PIL import Image


def correct_skew(file_path, angle, output_path):
    """Correct the skew of a file (PDF, image, TIFF) and save the output."""
    print(f"\n🔄 Correcting skew for: {file_path} (Angle: {angle:.2f}°)")

    corrected_images = []

    # Handle PDFs
    if file_path.lower().endswith(".pdf"):
        images = pdf2image.convert_from_path(file_path, dpi=300)
        if not images:
            print("❌ Failed to extract images from PDF.")
            raise ValueError(f"Failed to extract images from PDF: {file_path}")

        for idx, img in enumerate(images):
            print(f"🔹 Processing page {idx + 1}/{len(images)}...")
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            corrected_img_cv = rotate_image(img_cv, angle)
            corrected_img = Image.fromarray(cv2.cvtColor(corrected_img_cv, cv2.COLOR_BGR2RGB))
            corrected_images.append(corrected_img)

        save_as_pdf(corrected_images, output_path)
        print(f"✅ Corrected PDF saved: {output_path}")

    # Handle images (JPG, PNG, TIFF)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".tiff")):
        img = cv2.imread(file_path)
        corrected_img = rotate_image(img, angle)
        cv2.imwrite(output_path, corrected_img)
        print(f"✅ Corrected image saved: {output_path}")

    else:
        print("❌ Unsupported file format.")
        return


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
