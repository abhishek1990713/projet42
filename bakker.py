

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
os.environ["PATH"] += os.pathsep + gs_path  # Fixed typo

# Supported file extensions
IMAGE_EXTENSIONS = {'jpeg', 'tiff', 'tif', 'jpg', 'png'}
PDF_EXTENSIONS = {'pdf'}

def create_searchable_pdf(input_file_path, output_pdf_path):
    """Converts a PDF or image to a searchable PDF."""
    try:
        extension = input_file_path.split('.')[-1].lower()  # Normalize extension check
        print(f"Processing: {input_file_path} (Type: {extension})")

        if extension in PDF_EXTENSIONS:
            # Convert PDF to searchable PDF
            ocrmypdf.ocr(input_file_path, output_pdf_path, deskew=True, force_ocr=True, rotate_pages=True)

        elif extension in IMAGE_EXTENSIONS:
            print("Processing image file...")
            # Convert image to searchable PDF
            ocrmypdf.ocr(input_file_path, output_pdf_path, deskew=True, force_ocr=True, rotate_pages=True, image_dpi=300, pdf_renderer="hocr")

        print(f"✅ Searchable PDF created: {output_pdf_path}")

    except Exception as e:
        print(f"❌ Error processing {input_file_path}: {e}")

def process_folder(input_folder, output_folder):
    """Processes all PDFs and images in the input folder and saves searchable PDFs in the output folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Create output folder if it doesn't exist

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        if os.path.isfile(file_path):  # Ensure it's a file
            extension = filename.split('.')[-1].lower()
            if extension in PDF_EXTENSIONS or extension in IMAGE_EXTENSIONS:
                output_pdf_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_searchable.pdf")
                create_searchable_pdf(file_path, output_pdf_path)

# Define input and output folder paths
input_folder = r"/home/ko19678/japan_pipeline/pdfmyocr/input"
output_folder = r"/home/ko19678/japan_pipeline/pdfmyocr/output"

# Process all files in the input folder
process_folder(input_folder, output_folder)
