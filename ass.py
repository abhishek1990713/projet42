import os
import cv2
import numpy as np
import pdf2image
from PIL import Image


def correct_skew(file_path, angles, output_path):
    """Correct skew using detected angles for PDFs, images, and TIFFs."""
    print(f"\n🔄 Correcting skew for: {file_path}")

    corrected_images = []

    # Handle PDFs (Multiple Pages)
    if file_path.lower().endswith(".pdf"):
        images = pdf2image.convert_from_path(file_path, dpi=300)
        if not images:
            print("❌ Failed to extract images from PDF.")
            return

        for i, img in enumerate(images):
            page_no = i + 1
            angle = angles.get(page_no, 0.0)  # Get angle, default 0°
            print(f"  🔹 Processing page {page_no} | Angle: {angle:.2f}°")

            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            corrected_img_cv = rotate_image(img_cv, angle)
            corrected_img = Image.fromarray(cv2.cvtColor(corrected_img_cv, cv2.COLOR_BGR2RGB))
            corrected_images.append(corrected_img)

        save_as_pdf(corrected_images, output_path)
        print(f"✅ Corrected PDF saved: {output_path}")

    # Handle Images (Single Page)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".tiff")):
        angle = angles.get(1, 0.0)  # Only one image, get angle
        print(f"  🔹 Processing image | Angle: {angle:.2f}°")

        img = cv2.imread(file_path)
        corrected_img = rotate_image(img, angle)
        cv2.imwrite(output_path, corrected_img)
        print(f"✅ Corrected image saved: {output_path}")

    else:
        print("❌ Unsupported file format.")





import os
import cv2
import numpy as np
import pdf2image
from PIL import Image, TiffImagePlugin


def correct_skew(file_path, angles, output_path):
    """Correct skew for PDFs, TIFFs, and images using detected angles."""
    print(f"\n🔄 Correcting skew for: {file_path}")

    corrected_images = []

    # Handle PDFs (Multiple Pages)
    if file_path.lower().endswith(".pdf"):
        images = pdf2image.convert_from_path(file_path, dpi=300)
        if not images:
            print("❌ Failed to extract images from PDF.")
            return

        for i, img in enumerate(images):
            page_no = i + 1
            angle = angles.get(page_no, 0.0)  # Get angle, default 0°
            print(f"  🔹 Processing PDF page {page_no} | Angle: {angle:.2f}°")

            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            corrected_img_cv = rotate_image(img_cv, angle)
            corrected_img = Image.fromarray(cv2.cvtColor(corrected_img_cv, cv2.COLOR_BGR2RGB))
            corrected_images.append(corrected_img)

        save_as_pdf(corrected_images, output_path)
        print(f"✅ Corrected PDF saved: {output_path}")

    # Handle Multi-page TIFFs
    elif file_path.lower().endswith(".tiff"):
        with Image.open(file_path) as img:
            tiff_pages = []
            for i in range(img.n_frames):
                img.seek(i)  # Select TIFF page
                page_no = i + 1
                angle = angles.get(page_no, 0.0)
                print(f"  🔹 Processing TIFF page {page_no} | Angle: {angle:.2f}°")

                img_cv = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
                corrected_img_cv = rotate_image(img_cv, angle)
                corrected_img = Image.fromarray(cv2.cvtColor(corrected_img_cv, cv2.COLOR_BGR2RGB))
                tiff_pages.append(corrected_img)

        save_as_tiff(tiff_pages, output_path)
        print(f"✅ Corrected TIFF saved: {output_path}")

    # Handle Single-page Images (JPG, PNG, TIFF)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        angle = angles.get(1, 0.0)  # Only one image, get angle
        print(f"  🔹 Processing image | Angle: {angle:.2f}°")

        img = cv2.imread(file_path)
        corrected_img = rotate_image(img, angle)
        cv2.imwrite(output_path, corrected_img)
        print(f"✅ Corrected image saved: {output_path}")

    else:
        print("❌ Unsupported file format.")
        return


def rotate_image(image, angle):
    """Rotate image based on detected angle."""
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
    """Save images as a PDF."""
    images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)


def save_as_tiff(images, output_path):
    """Save multi-page TIFF images."""
    images[0].save(output_path, save_all=True, append_images=images[1:], compression="tiff_deflate")


# Example usage:
if __name__ == "__main__":
    # Example detected skew angles in dictionary format
    detected_angle = [
        {'page_no': 1, 'skewed_angle': 2.4523160457611084},
        {'page_no': 2, 'skewed_angle': 0.0},
        {'page_no': 3, 'skewed_angle': -1.9618529081344604},
        {'page_no': 4, 'skewed_angle': 0.0}
    ]

    # Convert list of dictionaries into a dictionary
    angles_dict = {entry['page_no']: entry['skewed_angle'] for entry in detected_angle}

    # Input and output file paths
    input_file = 











import os
import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image, TiffImagePlugin


def correct_skew(file_path, angles, output_path):
    """Correct skew for PDFs (directly rotating pages), TIFFs, and images."""
    print(f"\n🔄 Correcting skew for: {file_path}")

    # Handle PDFs (Rotate pages without converting to images)
    if file_path.lower().endswith(".pdf"):
        doc = fitz.open(file_path)

        for page_no in range(len(doc)):
            page = doc[page_no]
            angle = angles.get(page_no + 1, 0.0)  # PyMuPDF pages are 0-indexed
            print(f"  🔹 Rotating PDF page {page_no + 1} | Angle: {angle:.2f}°")
            page.set_rotation(int(angle))  # Rotates only by 90, 180, or 270 degrees

        doc.save(output_path)
        doc.close()
        print(f"✅ Corrected PDF saved: {output_path}")

    # Handle Multi-page TIFFs
    elif file_path.lower().endswith(".tiff"):
        with Image.open(file_path) as img:
            tiff_pages = []
            for i in range(img.n_frames):
                img.seek(i)  # Select TIFF page
                page_no = i + 1
                angle = angles.get(page_no, 0.0)
                print(f"  🔹 Processing TIFF page {page_no} | Angle: {angle:.2f}°")

                img_cv = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
                corrected_img_cv = rotate_image(img_cv, angle)
                corrected_img = Image.fromarray(cv2.cvtColor(corrected_img_cv, cv2.COLOR_BGR2RGB))
                tiff_pages.append(corrected_img)

        save_as_tiff(tiff_pages, output_path)
        print(f"✅ Corrected TIFF saved: {output_path}")

    # Handle Single-page Images (JPG, PNG, TIFF)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        angle = angles.get(1, 0.0)  # Only one image, get angle
        print(f"  🔹 Processing image | Angle: {angle:.2f}°")

        img = cv2.imread(file_path)
        corrected_img = rotate_image(img, angle)
        cv2.imwrite(output_path, corrected_img)
        print(f"✅ Corrected image saved: {output_path}")

    else:
        print("❌ Unsupported file format.")
        return


def rotate_image(image, angle):
    """Rotate image based on detected angle."""
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


def save_as_tiff(images, output_path):
    """Save multi-page TIFF images."""
    images[0].save(output_path, save_all=True, append_images=images[1:], compression="tiff_deflate")


# Example usage:
if __name__ == "__main__":
    # Example detected skew angles in dictionary format
    detected_angle = [
        {'page_no': 1, 'skewed_angle': 90},  # Must be 90, 180, or 270
        {'page_no': 2, 'skewed_angle': 0},
        {'page_no': 3, 'skewed_angle': 180},
        {'page_no': 4, 'skewed_angle': 0}
    ]

    # Convert list of dictionaries into a dictionary
    angles_dict = {entry['page_no']: entry['skewed_angle'] for entry in detected_angle}

    # Input and output file paths
    input_file = "sample.pdf"  # Change to your actual file (PDF, TIFF, JPG, etc.)
    output_file = "corrected_sample.pdf"  # Output corrected file

    # Call the function to correct skew
    correct_skew(input_file, angles_dict, output_file)
