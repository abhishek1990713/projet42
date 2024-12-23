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
    return Noneimport os
import cv2
import numpy as np
import pytesseract
import openpyxl
from openpyxl import Workbook

def get_image_size(image_path):
    return os.path.getsize(image_path)

def get_image_dpi(image_path):
    # Default DPI if not available
    return 300

def calculate_metrics(image):
    metrics = {}
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    metrics['image_size'] = image.size
    metrics['blurriness'] = cv2.Laplacian(gray, cv2.CV_64F).var()
    metrics['noise_level'] = np.mean(np.abs(gray - cv2.GaussianBlur(gray, (5, 5), 0)))
    return metrics

def extract_text_with_tesseract(image, lang="eng"):
    return pytesseract.image_to_string(image, lang=lang)

def is_colored(image):
    return len(image.shape) == 3 and image.shape[2] == 3

def adjust_brightness_contrast(image, brightness=0, contrast=0):
    return cv2.convertScaleAbs(image, alpha=1 + contrast / 100, beta=brightness)

def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

def blur_image(image):
    return cv2.GaussianBlur(image, (5, 5), 0)

def apply_threshold(image):
    _, thresholded = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    return thresholded

def morphological_operations(image):
    kernel = np.ones((3, 3), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

def change_dpi(image_path, output_path, target_dpi=300):
    image = cv2.imread(image_path)
    cv2.imwrite(output_path, image, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])

def calculate_psnr(original, processed):
    mse = np.mean((original - processed) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    return 20 * np.log10(max_pixel / np.sqrt(mse))

def calculate_ocr_performance(pre_text, post_text):
    return len(pre_text), len(post_text)

def save_metrics_to_excel(metric_list, excel_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Metrics"

    headers = [
        "Image Name", "Pre Original Size", "Pre Image Size", "Pre Blurriness",
        "Pre Noise Level", "Post Processed Size", "Post Image Size",
        "Post Blurriness", "Post Noise Level", "PSNR", "Pre OCR Text",
        "Post OCR Text", "Pre DPI", "Post DPI"
    ]
    ws.append(headers)

    for metrics in metric_list:
        row = [
            metrics['image_name'], metrics['pre_original_size'], metrics['pre_image_size'],
            metrics['pre_blurriness'], metrics['pre_noise_level'],
            metrics['post_processed_size'], metrics['post_image_size'],
            metrics['post_blurriness'], metrics['post_noise_level'],
            metrics['post_psnr'], metrics['pre_ocr_text'],
            metrics['post_ocr_text'], metrics['pre_dpi'], metrics['post_dpi']
        ]
        ws.append(row)

    wb.save(excel_path)

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
            print(f"\nProcessing image: {image_path}")

            image_name = os.path.basename(image_path)
            original_size = get_image_size(image_path)
            original_dpi = get_image_dpi(image_path)

            pre_metrics = calculate_metrics(image)
            pre_metrics['image_name'] = image_name
            pre_metrics['original_size'] = original_size
            pre_metrics['original_dpi'] = original_dpi

            original_ocr_text = extract_text_with_tesseract(image, lang=ocr_lang)
            print("\n--- OCR Result Before Processing ---")
            print(original_ocr_text)

            original_ocr_text_path = os.path.join(post_output_dir, f"{os.path.splitext(image_name)[0]}_original_ocr.txt")
            with open(original_ocr_text_path, 'w', encoding="utf-8") as f:
                f.write(original_ocr_text)

            if is_colored(image):
                print("Image is colored. Applying preprocessing...")
                adjusted = adjust_brightness_contrast(image, brightness=30, contrast=30)
                denoised = denoise_image(adjusted)
                preprocessed = denoised
            else:
                print("Image is black-and-white. Applying preprocessing...")
                blurred = blur_image(image)
                thresholded = apply_threshold(blurred)
                preprocessed = morphological_operations(thresholded)

            processed_image_path = os.path.join(post_output_dir, f"processed_{image_name}")
            cv2.imwrite(processed_image_path, preprocessed)

            processed_dpi = get_image_dpi(processed_image_path)
            if processed_dpi != 300:
                dpi_adjusted_path = os.path.join(post_output_dir, f"dpi_adjusted_{image_name}")
                change_dpi(processed_image_path, dpi_adjusted_path, target_dpi=300)
                processed_image_path = dpi_adjusted_path
                processed_dpi = 300

            processed_image = cv2.imread(processed_image_path)
            processed_ocr_text = extract_text_with_tesseract(processed_image, lang=ocr_lang)
            print("\n--- OCR Result After Processing ---")
            print(processed_ocr_text)

            processed_ocr_text_path = os.path.join(post_output_dir, f"{os.path.splitext(image_name)[0]}_processed_ocr.txt")
            with open(processed_ocr_text_path, 'w', encoding="utf-8") as f:
                f.write(processed_ocr_text)

            ocr_performance = calculate_ocr_performance(original_ocr_text, processed_ocr_text)

            post_metrics = calculate_metrics(processed_image)
            post_metrics['image_name'] = image_name
            post_metrics['processed_size'] = get_image_size(processed_image_path)
            post_metrics['psnr'] = f"{calculate_psnr(image, preprocessed):.2f} dB"

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
                'post_psnr': post_metrics['psnr'],
                'pre_ocr_text': original_ocr_text,
                'post_ocr_text': processed_ocr_text,
                'pre_dpi': pre_metrics['original_dpi'],
                'post_dpi': processed_dpi
            })

        except Exception as e:
            print(f"Error processing image: {image_path}. Error: {e}")
            continue

    if metric_list:
        save_metrics_to_excel(metric_list, excel_path)
        print("\nBatch processing completed. Metrics saved to Excel.")
    else:
        print("\nNo image processed successfully.")

# Set paths
input_folder = r"C:\CitiDev\preprocessing\Input"
output_dir = r"C:\CitiDev\preprocessing\Output"
excel_path = r"C:\CitiDev\preprocessing\Metrics.xlsx"
ocr_lang = 'eng'

process_image_from_folder(input_folder, output_dir, excel_path, ocr_lang)

print("\nImage preprocessing completed.")
