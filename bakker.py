
import os
from PyPDF2 import PdfReader, PdfWriter

def extract_pages_pypdf(pdf_path):
    # Get the folder and filename
    folder = os.path.dirname(pdf_path)
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Open the PDF
    reader = PdfReader(pdf_path)

    for page_num in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num])

        # Save the extracted page
        output_filename = os.path.join(folder, f"{file_name}_page_{page_num + 1}.pdf")
        with open(output_filename, "wb") as output_pdf:
            writer.write(output_pdf)
        
        print(f"Saved: {output_filename}")

# Example usage
input_folder = "path/to/input/folder"
for file in os.listdir(input_folder):
    if file.lower().endswith(".pdf"):
        extract_pages_pypdf(os.path.join(input_folder, file))
