

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

df = parse_mrz(mrl1, mrl2)
print(df)

import ocrmypdf
import os

# Set input and output folders
input_folder = r"/home/ko19678/japan_pipeline/pdfmyocr/input"
output_folder = r"/home/ko19678/japan_pipeline/pdfmyocr/output"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

def create_searchable_pdf(input_file_path, output_file_path):
    try:
        extension = input_file_path.split('.')[-1].lower()  # Get file extension
        print(f"📄 Processing: {input_file_path}")

        # Common OCR parameters
        ocr_params = dict(
            language="jpn+eng",  # Supports both Japanese & English OCR
            force_ocr=True,  # Force OCR even if text exists
            redo_ocr=True,  # Remove old OCR layers before applying new
            deskew=True,  # Fix skewed text
            rotate_pages=True,  # Auto-rotate misaligned pages
            rotate_pages_threshold=5.0,  # Rotation confidence threshold
            remove_background=True,  # Remove noise from scanned pages
            clean=True,  # Remove speckles & unwanted marks
            clean_final=True,  # Additional post-cleaning
            optimize=3,  # Maximum compression without losing quality
            pdfa=True,  # Create PDF/A (long-term archive standard)
            pdfa_image_compression="lossless",  # No quality loss
            jpeg_quality=92,  # High-quality JPEG compression
            image_dpi=300,  # High DPI for accurate OCR on images
            pdf_renderer="hocr",  # Ensure better text overlay in PDF
            progress_bar=True,  # Show progress bar
            jobs=4  # Parallel processing for speed
        )

        if extension in ['pdf']:
            ocrmypdf.ocr(input_file_path, output_file_path, **ocr_params)

        elif extension in ['jpeg', 'jpg', 'png', 'tiff', 'tif']:
            print("🖼️ Processing image file")
            ocrmypdf.ocr(input_file_path, output_file_path, **ocr_params)

        print(f"✅ Searchable PDF created: {output_file_path}")

    except Exception as e:
        print(f"❌ Error processing {input_file_path}: {e}")

# Process all files in the input folder
for filename in os.listdir(input_folder):
    input_file_path = os.path.join(input_folder, filename)
    output_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_searchable.pdf")

    # Ensure it's a file (not a folder)
    if os.path.isfile(input_file_path):
        create_searchable_pdf(input_file_path, output_file_path)

print("🎯 All files processed successfully.")

