

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

df = parse_mrz(mrl1, mrl2)
print(df)

import ocrmypdf
import pytesseract
import pdfplumber
import json
import os

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Set Ghostscript path
gs_path = r"/home/ko19678/.conda/pkgs/ghostscript-10.04.0-h5888daf_0/bin"
os.environ["PATH"] += os.pathsep + gs_path

def generate_json(output_pdf_path, output_folder):
    """Extract text from a searchable PDF and save it as a JSON file."""
    try:
        with pdfplumber.open(output_pdf_path) as pdf:
            words_data = []

            for page_number, page in enumerate(pdf.pages, start=1):
                words = page.extract_words()

                for word in words:
                    word_info = {
                        "word": word["text"],
                        "x": int(word["x0"]),
                        "y": int(word["top"]),
                        "width": int(word["x1"]) - int(word["x0"]),
                        "height": int(word["bottom"]) - int(word["top"]),
                        "page": page_number
                    }
                    words_data.append(word_info)

        output_json_path = os.path.join(output_folder, f"{os.path.basename(output_pdf_path).split('.')[0]}.json")

        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(words_data, json_file, indent=4)

        print(f"JSON file created successfully: {output_json_path}")

    except Exception as e:
        print(f"Error in generate_json: {e}")

def create_searchable_pdf(input_file_path, output_folder):
    """Convert a PDF or image into a searchable PDF and generate a JSON file."""
    try:
        extension = input_file_path.split('.')[-1].lower()
        print(f"Processing file: {input_file_path} (Extension: {extension})")

        output_pdf_path = os.path.join(output_folder, f"{os.path.basename(input_file_path).split('.')[0]}.pdf")

        if extension in ['pdf']:
            ocrmypdf.ocr(input_file_path, output_pdf_path, deskew=True, force_ocr=True, rotate_pages=True)

        elif extension in ['jpeg', 'jpg', 'png', 'tiff', 'tif']:
            ocrmypdf.ocr(input_file_path, output_pdf_path, deskew=True, force_ocr=True, rotate_pages=True, image_dpi=300)

        print(f"Searchable PDF created successfully: {output_pdf_path}")

        # Generate JSON file
        generate_json(output_pdf_path, output_folder)

    except Exception as e:
        print(f"Error in create_searchable_pdf: {e}")

def process_all_files(input_folder, output_folder):
    """Read all PDFs and images from the input folder and process them."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)

        if os.path.isfile(file_path):
            extension = file_name.split('.')[-1].lower()

            if extension in ['pdf', 'jpeg', 'jpg', 'png', 'tiff', 'tif']:
                create_searchable_pdf(file_path, output_folder)

# Define input and output folders
input_folder = r"/home/ko19678/japan_pipeline/pdfmyocr/input"
output_folder = r"/home/ko19678/japan_pipeline/pdfmyocr/output"

# Process all files in the input folder
process_all_files(input_folder, output_folder)
