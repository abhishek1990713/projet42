
import os
import numpy as np
from PIL import Image
import onnxruntime as ort
import fitz  # PyMuPDF

def load_model(model_path):
    return ort.InferenceSession(model_path)

def preprocess_image(image):
    image = image.convert("RGB").resize((224, 224))
    image_np = np.array(image).astype(np.float32) / 255.0
    image_np = image_np.transpose(2, 0, 1)  # Channel first
    return image_np[np.newaxis, :]  # Add batch dimension

def predict_angle(session, image):
    input_array = preprocess_image(image)
    result = session.run(None, {"input": input_array})
    return float(result[0].squeeze())

def process_pdf(pdf_path, session):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        angle = predict_angle(session, image)
        print(f"📄 Page {page_num+1}: Predicted orientation angle: {angle:.2f}°")
    doc.close()

def process_image(image_path, session):
    image = Image.open(image_path)
    angle = predict_angle(session, image)
    print(f"🖼️ Image: Predicted orientation angle: {angle:.2f}°")

if __name__ == "__main__":
    model_path = "deep_oad_model.onnx"
    file_path = "sample.pdf"  # or "sample_image.jpg"

    session = load_model(model_path)

    if file_path.lower().endswith(".pdf"):
        process_pdf(file_path, session)
    else:
        process_image(file_path, session)
