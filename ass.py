from flask import Flask, redirect, url_for, request, render_template, jsonify
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
from flask_cors import CORS, cross_origin
import boto3
import glob

app = Flask(__name__)

CORS(app)


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index4.html')


@app.route('/predict', methods=['GET'])
def Upload():
    if request.method == 'GET':
        # print(request.json['file'])


        r = sr.Recognizer()

        sound = AudioSegment.from_wav("inp/splite.wav")

        audio_chunks = split_on_silence(sound, min_silence_len=1000, silence_thresh=sound.dBFS - 14, keep_silence=500)
        whole_text = ""
        textMap = {}
        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join('InputFiles', f"speech_chunk{i}.wav")
            print("Exporting file", output_file)
            result = chunk.export(output_file, format="wav")




        # os.remove("inp/splite.wav")
        return str(result)

    # return str(result)
    return None

import cv2
import numpy as np
import os
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
from sklearn import metrics
import shutil

# Tesseract configuration (ensure Tesseract OCR is correctly installed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to adjust brightness and contrast
def adjust_brightness_contrast(image, brightness=0, contrast=0):
    image = np.int16(image)
    image = image * (contrast / 127 + 1) - contrast + brightness
    image = np.clip(image, 0, 255)
    return np.uint8(image)

# Function to denoise image
def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

# Function to apply thresholding
def apply_threshold(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

# Function to apply morphological operations
def morphological_operations(image):
    kernel = np.ones((3, 3), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    return image

# Function to resize the image
def resize_image(image, width, height):
    return cv2.resize(image, (width, height))

# Function to check if the image is colored
def is_colored(image):
    if len(image.shape) == 2:
        return False
    elif len(image.shape) == 3:
        b, g, r = cv2.split(image)
        return not (np.array_equal(b, g) and np.array_equal(b, r))
    else:
        raise ValueError("Unsupported image format")

# Function to save processed images and show them
def save_and_show(images, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filenames = []
    for i, (desc, img) in enumerate(images):
        filename = os.path.join(output_dir, f'{desc}.jpg')
        cv2.imwrite(filename, img)
        filenames.append(filename)
        print(f"Saved: {filename}")
    return filenames

# Function to extract text with Tesseract
def extract_text_with_tesseract(image, lang='eng'):
    try:
        config = "--psm 3"
        text = pytesseract.image_to_string(image, config=config, lang=lang)
        print(f"Extracted text: {text}")
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

# Function to calculate image metrics
def calculate_metrics(image):
    metrics_dict = {}
    metrics_dict['image_size'] = f"{image.shape[1]} x {image.shape[0]}"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    metrics_dict['blurriness'] = laplacian_var
    noise_estimation = np.std(image)
    metrics_dict['noise_level'] = noise_estimation
    return metrics_dict

# Function to calculate image size
def get_image_size(file_path):
    size_in_bytes = os.path.getsize(file_path)
    size_in_kb = size_in_bytes / 1024
    size_in_mb = size_in_kb / 1024
    if size_in_mb >= 1:
        return f"{size_in_mb:.2f} MB"
    else:
        return f"{size_in_kb:.2f} KB"

# Function to save metrics to Excel
def save_metrics_to_excel(metrics_list, excel_path):
    df = pd.DataFrame(metrics_list)
    df.to_excel(excel_path, index=False, engine='openpyxl')
    print(f"Metrics saved to: {excel_path}")

# Function to calculate PSNR
def calculate_psnr(original, processed):
    mse = np.mean((original - processed) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 10 * np.log10(max_pixel ** 2 / mse)
    return psnr

# Convert PDF to images
def convert_pdf_to_images(pdf_path):
    try:
        images = convert_from_path(pdf_path, 300)  # Convert PDF to images at 300 DPI
        image_list = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"page_{i + 1}.png")
            image.save(image_path, 'PNG')
            image_list.append(image_path)
        return image_list
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

# Main function to process images or PDFs
def process_input(input_path, output_dir, excel_path, ocr_lang="eng"):
    metric_list = []

    if input_path.lower().endswith('.pdf'):
        image_paths = convert_pdf_to_images(input_path)
    else:
        valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
        image_paths = [os.path.join(input_path, file) for file in os.listdir(input_path) if file.lower().endswith(valid_extensions)]

    if not image_paths:
        print(f"No images found in the input: {input_path}")
        return

    for image_path in image_paths:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}. Skipping...")
            continue

        print(f"Processing image: {image_path}")
        pre_metrics = calculate_metrics(image)
        pre_metrics['image_name'] = os.path.basename(image_path)
        pre_metrics['original_size'] = get_image_size(image_path)

        if is_colored(image):
            print("Image is colored. Applying preprocessing...")
            denoised = denoise_image(image)
            adjusted = adjust_brightness_contrast(denoised, brightness=30, contrast=30)
            preprocessed = adjusted
        else:
            print("Image is black-and-white. Applying preprocessing...")
            blurred = cv2.GaussianBlur(image, (5, 5), 0)
            thresholded = apply_threshold(blurred)
            preprocessed = thresholded

        if preprocessed is None:
            print(f"Preprocessing failed for {image_path}")
            continue

        morphed = morphological_operations(preprocessed)
        if morphed is None:
            print(f"Morphological operation failed for {image_path}")
            continue

        processed_image_path = os.path.join(output_dir, f"processed_{os.path.basename(image_path)}")
        cv2.imwrite(processed_image_path, morphed)

        post_metrics = calculate_metrics(morphed)
        post_metrics['image_name'] = os.path.basename(image_path)
        post_metrics['processed_size'] = get_image_size(processed_image_path)

        psnr_value = calculate_psnr(image, morphed)
        post_metrics['psnr'] = f"{psnr_value:.2f} dB"

        ocr_text = extract_text_with_tesseract(morphed, lang=ocr_lang)
        ocr_text_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}.txt")
        with open(ocr_text_path, 'w', encoding='utf-8') as f:
            f.write(ocr_text)

        combined_metrics = {**pre_metrics, **post_metrics}
        metric_list.append(combined_metrics)

    if metric_list:
        save_metrics_to_excel(metric_list, excel_path)
        print(f"Metrics saved to: {excel_path}")
    else:
        print("No images processed successfully.")

# Example usage
input_path = "C:\\path\\to\\input"  # Folder or PDF path
output_dir = "C:\\path\\to\\output"
excel_path = "C:\\path\\to\\save\\metrics.xlsx"

process_input(input_path, output_dir, excel_path, ocr_lang="eng")

