⁸

mrl1 = 



import aspose.ocr as ocr

# Instantiate Aspose.OCR API
api = ocr.AsposeOCR()

# File path (Change as needed)
file_path = r"\\apachlowinrv7933\odp\Senduran\New folder\Process\Testing\Input\skewed\Skewed- Payment advice.pdf"

# Determine input type (PDF or image)
input_type = ocr.InputType.PDF if file_path.lower().endswith(".pdf") else ocr.InputType.SINGLE_IMAGE

# Add file to OCR batch
ocr_input = ocr.OcrInput(input_type)
ocr_input.add(file_path)

# Detect skew angle
angles = api.calculate_skew(ocr_input)

# Print skew angles
for angle in angles:
    print(f"File: {angle.source}")
    print(f"Skew angle: {angle.angle:.1f}°")

# Perform OCR and extract text
extracted_text = api.recognize(ocr_input)
print("\nExtracted Text:\n", extracted_text)
