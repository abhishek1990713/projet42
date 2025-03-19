

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

df = parse_mrz(mrl1, mrl2)
print(df)

import os
import ocrmypdf
import pytesseract

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Set the Poppler path
poppler_path = r"/home/ko19678/.conda/pkgs/poppler-23.08.0-habdc1e1_3/bin"
os.environ["PATH"] += os.pathsep + poppler_path

# Set the Ghostscript path
gs_path = r"/home/ko19678/.conda/pkgs/ghostscript-10.04.0-h5888daf_0/bin"
os.environ["PATH"] += os.pathsep + gs_path  

# Supported file extensions
IMAGE_EXTENSIONS = {'jpeg', 'tiff', 'tif', 'jpg', 'png'}
PDF_EXTENSIONS = {'pdf'}

# Toggle Parameters (Enable/Disable Features)
ENABLE_OPTIONS = {
    "language": "eng+jpn",  # English + Japanese OCR
    "deskew": True,  # Fix skewed pages
    "rotate_pages": True,  # Auto-rotate pages
    "remove_background": True,  # Remove noise from scans
    "optimize": 3,  # Maximum PDF optimization
    "output_type": "pdfa",  # Save as PDF/A (archival)
    "force_ocr": True,  # OCR everything, even text PDFs
    "skip_text": False,  # OCR even if text is already present
    "redo_ocr": True,  # Always re-run OCR
    "clean": True,  # Remove artifacts
    "pdf_renderer": "sandwich",  # Best rendering mode
    "image_dpi": 300,  # High DPI for images
    "tesseract_oem": 1,  # Tesseract OCR engine mode
    "tesseract_timeout": 600,  # Timeout for OCR (10 min)
    "rotate_pages_threshold": 5.0,  # Confidence threshold for rotation
    "remove_vectors": True,  # Remove vector graphics
    "jpeg_quality": 90,  # Image compression quality
    "fast_web_view": True,  # Enable fast web viewing
    "keep_temporary_files": False,  # Delete temp files
    "sidecar": None,  # No extra text file output
}

def create_searchable_pdf(input_file_path, output_pdf_path):
    """Converts PDFs and images into fully optimized searchable PDFs with all available parameters."""
    try:
        extension = input_file_path.split('.')[-1].lower()
        print(f"Processing: {input_file_path} (Type: {extension})")

        if extension in PDF_EXTENSIONS or extension in IMAGE_EXTENSIONS:
            # Process file with all parameters
            ocrmypdf.ocr(input_file_path, output_pdf_path, **ENABLE_OPTIONS)
            print(f"✅ Searchable PDF created: {output_pdf_path}")

    except Exception as e:
        print(f"❌ Error processing {input_file_path}: {e}")

def process_folder(input_folder, output_folder):
    """Processes all PDFs and images in the input folder and saves searchable PDFs in the output folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Create output folder if it doesn't exist

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path):
            extension = filename.split('.')[-1].lower()
            if extension in PDF_EXTENSIONS or extension in IMAGE_EXTENSIONS:
                output_pdf_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_searchable.pdf")
                create_searchable_pdf(file_path, output_pdf_path)

# Define input and output folder paths
input_folder = r"/home/ko19678/japan_pipeline/pdfmyocr/input"
output_folder = r"/home/ko19678/japan_pipeline/pdfmyocr/output"

# Process all files in the input folder
process_folder(input_folder, output_folder)

