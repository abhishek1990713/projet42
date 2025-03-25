import ocrmypdf
import pytesseract
import pdfplumber
import json
import os
import pandas as pd
from pathlib import Path
from time import time
from script_aspose_ocr import process_document  # Ensure this function exists in script_aspose_ocr.py

# Set Tesseract-OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set Ghostscript path for Linux (if needed)
gs_path = r"/home/ko19678/.conda/pkgs/ghostscript-10.04.0-h5888daf_0/bin"
os.environ["PATH"] += os.pathsep + gs_path


def generate_json(output_pdf_path, output_folder):
    """Extracts text and coordinates from a searchable PDF and saves to JSON."""
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

        output_json_path = os.path.join(output_folder, f"{Path(output_pdf_path).stem}.json")
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(words_data, json_file, indent=4, ensure_ascii=False)

        print(f"JSON file created: {output_json_path}")
    except Exception as e:
        print(f"Error generating JSON: {e}")


def create_searchable_pdf(input_file_path, output_folder):
    """Converts an image or non-searchable PDF to a searchable PDF."""
    try:
        extension = input_file_path.split('.')[-1].lower()
        print(f"Processing file: {input_file_path} (Extension: {extension})")

        output_pdf_path = os.path.join(output_folder, f"{Path(input_file_path).stem}_ocrmypdf.pdf")

        if extension in ['pdf']:
            ocrmypdf.ocr(input_file_path, output_pdf_path, deskew=True, force_ocr=True, rotate_pages=True)
        elif extension in ['jpeg', 'tiff', 'tif', 'jpg', 'png']:
            ocrmypdf.ocr(input_file_path, output_pdf_path, deskew=True, force_ocr=True, rotate_pages=True, image_dpi=300, pdf_renderer="hocr")
        else:
            print(f"Unsupported file type: {extension}")
            return None

        print(f"Searchable PDF created: {output_pdf_path}")
        return output_pdf_path

    except Exception as e:
        print(f"Error creating searchable PDF: {e}")
        return None


# Define input/output directories
input_folder_path = r"/home/ko19678/japan_pipeline/rotate/input"
output_folder = r"/home/ko19678/japan_pipeline/rotate/output"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Track execution times
execution_data = []

# Process each file in the input folder
for file_name in os.listdir(input_folder_path):
    if os.path.isfile(os.path.join(input_folder_path, file_name)):
        print(f"Processing file: {file_name}")

        input_file_path = os.path.join(input_folder_path, file_name)

        # Step 1: Rotation Correction using Aspose OCR
        rotation_start_time = time()
        rotation_corrected_file = process_document(input_file_path, output_folder)  # Calls script_aspose_ocr.py
        rotation_end_time = time()
        rotation_time = round(rotation_end_time - rotation_start_time, 2)

        print(f"Rotation correction completed for {file_name} in {rotation_time} seconds")

        # Step 2: Convert to Searchable PDF
        pdf_start_time = time()
        output_pdf_path = create_searchable_pdf(rotation_corrected_file, output_folder)
        pdf_end_time = time()
        pdf_time = round(pdf_end_time - pdf_start_time, 2)

        if output_pdf_path:
            print(f"Searchable PDF created for {file_name} in {pdf_time} seconds")

            # Step 3: Generate JSON Output
            json_start_time = time()
            generate_json(output_pdf_path, output_folder)
            json_end_time = time()
            json_time = round(json_end_time - json_start_time, 2)

            print(f"JSON extraction completed for {file_name} in {json_time} seconds")

            # Step 4: Store execution times
            execution_data.append({
                "fileName": file_name,
                "RotationCorrectionTime": rotation_time,
                "PdfExecutionTime": pdf_time,
                "JsonExecutionTime": json_time
            })

# Save execution times to CSV
df = pd.DataFrame(execution_data)
csv_path = os.path.join(output_folder, "execution_times.csv")
df.to_csv(csv_path, index=False)

print(f"Execution times saved to {csv_path}")
