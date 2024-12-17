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


if __name__ == '__main__':
    app.run(debug=True)
import cv2
import numpy as np
import os
import pytesseract
import pandas as pd
from sklearn import metrics

# Tesseract command setup
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to adjust brightness and contrast
def adjust_brightness_contrast(image, brightness=0, contrast=0):
    image = np.int16(image)
    image = image * (contrast / 127 + 1) - contrast + brightness
    image = np.clip(image, 0, 255)
    return np.uint8(image)

# Function to denoise image
def denoise_image(image):
    if len(image.shape) == 3:
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    else:
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

# Function to blur image
def blur_image(image):
    return cv2.GaussianBlur(image, (5, 5), 0)

# Function to apply thresholding
def apply_threshold(image):
    # Ensure image is grayscale before thresholding
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image  # If it's already grayscale, no need to convert

    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return thresh

# Function to apply morphological operations
def morphological_operations(image):
    kernel = np.ones((3, 3), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    return image

# Function to check if the image is colored
def is_colored(image):
    return len(image.shape) == 3

# Function to save images and show
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

# Function to get image size
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
    print(f"Metrics saved as: {excel_path}")

# Function to calculate PSNR
def calculate_psnr(original, processed):
    mse = np.mean((original - processed) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 10 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

# Function to process images from a folder
def process_image_from_folder(input_folder, output_dir, excel_path, ocr_lang="eng"):
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    image_paths = [os.path.join(input_folder, file) for file in os.listdir(input_folder) if file.lower().endswith(valid_extensions)]
    
    if not image_paths:
        raise ValueError(f"No image files found in the folder: {input_folder}")
    
    post_output_dir = os.path.join(output_dir, "PostProcessed")
    os.makedirs(post_output_dir, exist_ok=True)
    metric_list = []

    for image_path in image_paths:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}. Skipping...")
            continue
        
        try:
            print(f"Processing image: {image_path}")
            image_name = os.path.basename(image_path)
            original_size = get_image_size(image_path)
            
            # Pre-metrics
            pre_metrics = calculate_metrics(image)
            pre_metrics['original_size'] = original_size
            
            if is_colored(image):
                print("Image is colored. Applying preprocessing...")
                denoised = denoise_image(image)
                adjusted = adjust_brightness_contrast(denoised, brightness=30, contrast=30)
                preprocessed = adjusted
            else:
                print("Image is black-and-white. Applying preprocessing...")
                blurred = blur_image(image)
                preprocessed = apply_threshold(blurred)
            
            # Morphological operations
            morphed = morphological_operations(preprocessed)
            processed_image_path = os.path.join(post_output_dir, f"processed_{image_name}")
            cv2.imwrite(processed_image_path, morphed)
            
            # Post-processing metrics
            post_metrics = calculate_metrics(morphed)
            post_metrics['processed_size'] = get_image_size(processed_image_path)
            post_metrics['psnr'] = f"{calculate_psnr(image, morphed):.2f} dB"
            
            # Add metrics to list in the specified sequence
            metric_list.append({
                'image_name': image_name,
                'pre_original_size': pre_metrics['original_size'],
                'pre_image_size': pre_metrics['image_size'],
                'pre_blurriness': pre_metrics['blurriness'],
                'pre_noise_level': pre_metrics['noise_level'],
                'post_processed_size': post_metrics['processed_size'],
                'post_image_size': post_metrics['image_size'],
                'post_blurriness': post_metrics['blurriness'],
                'post_noise_level': post_metrics['noise_level'],
                'pre_psnr': 'N/A',  # PSNR is not applicable for pre-processing
                'post_psnr': post_metrics['psnr']
            })
        except Exception as e:
            print(f"Error processing image: {image_path}. Error: {e}")
            continue
    
    # Save metrics to Excel
    if metric_list:
        save_metrics_to_excel(metric_list, excel_path)
        print("Batch processing completed. Metrics saved to Excel.")
    else:
        print("No image processed successfully.")

# Example usage
input_folder = r"C:\CitiDev\Passport_new"
output_dir = r"C:\CitiDev\Passport_new\Processed"
excel_path = r"C:\CitiDev\Passport_new\metrics.xlsx"
ocr_lang = 'eng'

process_image_from_folder(input_folder, output_dir, excel_path, ocr_lang)

