⁸

mrl1 = 



import aspose.ocr as ocr

# Instantiate Aspose.OCR API
api = ocr.AsposeOCR()

# File path (Change as needed)
file_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\Skewed- Payment advice.pdf"

# Determine input type
input_type = ocr.InputType.PDF if file_path.lower().endswith(".pdf") else ocr.InputType.SINGLE_IMAGE

# Add file to OCR batch
ocr_input = ocr.OcrInput(input_type)
ocr_input.add(file_path)

# Detect skew angle for all pages
angles = api.calculate_skew(ocr_input)

print("\nSkew Angles Detected:")
for angle in angles:
    print(f"File: {angle.source}, Page: {angle.page_number}, Skew Angle: {angle.angle:.1f}°")

# Perform OCR and extract text from all pages
extracted_text = api.recognize(ocr_input)

print("\nExtracted Text from PDF:")
for page_num, text in enumerate(extracted_text.split("\f"), start=1):  # '\f' is a page break
    print(f"\n--- Page {page_num} ---\n{text}")
