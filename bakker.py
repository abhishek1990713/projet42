import os
import pdf2image
import aspose.ocr as ocr


def detect_skew_angle(pdf_path):
    """Detect the skew angle for the first page of a PDF using OCR."""
    print(f"\n📄 Processing PDF for skew detection: {pdf_path}")

    images = pdf2image.convert_from_path(pdf_path, dpi=300)
    if not images:
        print("❌ Failed to extract images from PDF.")
        raise ValueError(f"Failed to extract images from PDF: {pdf_path}")

    temp_image_path = "temp_angle_detect.png"
    images[0].save(temp_image_path)  # Save first page as an image

    print(f"🖼️ Extracted first page for OCR skew detection: {temp_image_path}")

    api = ocr.AsposeOcr()
    ocr_input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
    ocr_input.add(temp_image_path)

    angles = api.calculate_skew(ocr_input)

    # Clean up temporary image
    os.remove(temp_image_path)

    if angles:
        skew_angle = angles[0].angle
        print(f"✅ Detected skew angle: {skew_angle:.2f}° for {pdf_path}")
        return skew_angle
    else:
        print(f"ℹ️ No skew detected for {pdf_path}")
        return 0  # No skew detected, return 0 degrees
