

import fitz  # PyMuPDF for direct PDF handling
import os
import cv2
import numpy as np
from PIL import Image


def correct_skew(file_path, angles, output_path):
    """Correct skew for PDFs, TIFFs, and Images directly."""
    file_extension = file_path.split('.')[-1].upper()
    print(f"\n🔄 Processing Document: {file_path}")
    print(f"📂 Document Type: {file_extension}")

    # Handle PDFs (Multi-page) without converting to images
    if file_path.lower().endswith(".pdf"):
        doc = fitz.open(file_path)
        total_pages = len(doc)
        print(f"📄 Total Pages in PDF: {total_pages}")

        for i, page in enumerate(doc):
            page_no = i + 1
            angle = angles.get(page_no, 0.0)

            print(f"  🔹 Processing PDF Page {page_no}/{total_pages} | Type: PDF Page | Detected Angle: {angle:.2f}°")

            # Rotate the page directly
            page.set_rotation(int(angle))  # FitZ rotates in 90-degree increments, so round off if needed.

        doc.save(output_path)
        doc.close()
        print(f"✅ Corrected PDF saved: {output_path}")

    # Handle Multi-page TIFFs
    elif file_path.lower().endswith(".tiff"):
        with Image.open(file_path) as img:
            total_frames = img.n_frames
            print(f"🖼️ Total Pages in TIFF: {total_frames}")

            tiff_pages = []
            for i in range(total_frames):
                img.seek(i)
                page_no = i + 1
                angle = angles.get(page_no, 0.0)

                print(f"  🔹 Processing TIFF Page {page_no}/{total_frames} | Type: TIFF Frame | Detected Angle: {angle:.2f}°")

                img_cv = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
                corrected_img_cv = rotate_image(img_cv, angle)
                corrected_img = Image.fromarray(cv2.cvtColor(corrected_img_cv, cv2.COLOR_BGR2RGB))
                tiff_pages.append(corrected_img)

        save_as_tiff(tiff_pages, output_path)
        print(f"✅ Corrected TIFF saved: {output_path}")

    # Handle Single-page Images (JPG, PNG, TIFF)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        angle = angles.get(1, 0.0)
        print(f"  🔹 Processing Image File | Type: Single Image | Detected Angle: {angle:.2f}°")

        img = cv2.imread(file_path)
        corrected_img = rotate_image(img, angle)
        cv2.imwrite(output_path, corrected_img)
        print(f"✅ Corrected Image saved: {output_path}")

    else:
        print("❌ Unsupported file format.")
        return


def rotate_image(image, angle):
    """Rotate image based on detected angle."""
    print(f"  ↪ Rotating Image by {angle:.2f}°")

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


def save_as_tiff(images, output_path):
    """Save multi-page TIFF images."""
    print(f"🖼️ Saving {len(images)} pages as a TIFF...")
    images[0].save(output_path, save_all=True, append_images=images[1:], compression="tiff_deflate")


# Example usage:
if __name__ == "__main__":
    detected_angle = [
        {'page_no': 1, 'skewed_angle': 2.45},
        {'page_no': 2, 'skewed_angle': 0.0},
        {'page_no': 3, 'skewed_angle': -1.96},
        {'page_no': 4, 'skewed_angle': 0.0}
    ]

    angles_dict = {entry['page_no']: entry['skewed_angle'] for entry in detected_angle}

    input_file = "abc.pdf"  # Change to your actual file (PDF, TIFF, JPG, etc.)
    output_file = "corrected_abc.pdf"

    correct_skew(input_file, angles_dict, output_file)
