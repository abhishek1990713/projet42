

import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
import pdfplumber

def is_pdf_searchable_advanced(pdf_path):
    doc = fitz.open(pdf_path)
    searchable_pages = []
    non_searchable_pages = []
    image_based_pages = []
    
    for page_num in range(len(doc)):
        text_pymupdf = doc[page_num].get_text("text")  # Extract text using PyMuPDF
        text_pdfminer = extract_text(pdf_path, page_numbers=[page_num])  # Extract using pdfminer
        
        # Use pdfplumber to detect image-based pages
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_num]
            images = page.images  # Get images on the page
        
        if text_pymupdf.strip() or text_pdfminer.strip():
            searchable_pages.append(page_num + 1)
        elif images:
            image_based_pages.append(page_num + 1)
        else:
            non_searchable_pages.append(page_num + 1)

    print(f"Searchable Pages: {searchable_pages}")
    print(f"Image-Based Pages (Likely Scanned): {image_based_pages}")
    print(f"Non-Searchable Pages: {non_searchable_pages}")

    return len(searchable_pages) > 0, searchable_pages, image_based_pages, non_searchable_pages

# Example usage
pdf_path = "sample.pdf"  # Replace with your PDF file path
is_searchable, searchable_pages, image_based_pages, non_searchable_pages = is_pdf_searchable_advanced(pdf_path)

if is_searchable:
    print("The PDF contains searchable text.")
else:
    print("The PDF is not searchable and likely needs OCR.")
