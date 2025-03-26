import os
import cv2
import numpy as np
import pdf2image
from PIL import Image


def correct_skew(file_path, angles, output_path):
    """Correct skew using detected angles for PDFs, images, and TIFFs."""
    print(f"\n🔄 Correcting skew for: {file_path}")

    corrected_images = []

    # Handle PDFs (Multiple Pages)
    if file_path.lower().endswith(".pdf"):
        images = pdf2image.convert_from_path(file_path, dpi=300)
        if not images:
            print("❌ Failed to extract images from PDF.")
            return

        for i, img in enumerate(images):
            page_no = i + 1
            angle = angles.get(page_no, 0.0)  # Get angle, default 0°
            print(f"  🔹 Processing page {page_no} | Angle: {angle:.2f}°")

            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            corrected_img_cv = rotate_image(img_cv, angle)
            corrected_img = Image.fromarray(cv2.cvtColor(corrected_img_cv, cv2.COLOR_BGR2RGB))
            corrected_images.append(corrected_img)

        save_as_pdf(corrected_images, output_path)
        print(f"✅ Corrected PDF saved: {output_path}")

    # Handle Images (Single Page)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".tiff")):
        angle = angles.get(1, 0.0)  # Only one image, get angle
        print(f"  🔹 Processing image | Angle: {angle:.2f}°")

        img = cv2.imread(file_path)
        corrected_img = rotate_image(img, angle)
        cv2.imwrite(output_path, corrected_img)
        print(f"✅ Corrected image saved: {output_path}")

    else:
        print("❌ Unsupported file format.")
        return


def rotate_image(image, angle):
    """Rotate image based on detected angle."""
    print(f"  ↪ Rotating image by {angle:.2f}°")

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    abs_cos = abs(np.cos(np.radians(angle)))
    abs_sin = abs(np.sin(np.radians(angle)))

    bound_w = int(h * abs_sin + w * abs_cos)
    bound_h = int(h * abs_cos + w * abs_sin)

    M = cv2.getRotationMatrix2D(center, angle, 1)
    M[0, 2] += (bound_w / 2) - center[0]
    M[1, 2] += (bound_h / 2) - center[1]

    rotated = cv2.warpAffine(image, M, (bound_w, bound_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def save_as_pdf(images, output_path):
    """Save images as a PDF."""
    images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)


# Example usage:
if __name__ == "__main__":
    # Example detected skew angles in dictionary format
    detected_angle = [
        {'page_no': 1, 'skewed_angle': 2.4523160457611084},
        {'page_no': 2, 'skewed_angle': 0.0},
        {'page_no': 3, 'skewed_angle': -1.9618529081344604},
        {'page_no': 4, 'skewed_angle': 0.0}
    ]

    # Convert list of dictionaries into a dictionary
    angles_dict = {entry['page_no']: entry['skewed_angle'] for entry in detected_angle}

    # Input and output file paths
    input_file = "sample.pdf"  # Change to your actual PDF file path
    output_file = "corrected_sample.pdf"  # Output corrected file name

    # Call the function to correct skew
    correct_skew(input_file, angles_dict, output_file)


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

import os
import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Load language detection model (fastText)
pretrained_lang_model = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
lang_model = fasttext.load_model(pretrained_lang_model)

# Translation model checkpoint
checkpoint = r"C:\CitiDev\language_prediction\m2m"
translation_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Translation pipeline
translation_pipeline = pipeline(
    'translation', 
    model=translation_model, 
    tokenizer=tokenizer, 
    max_length=400
)

# Input folder path
input_folder = r"C:\CitiDev\language_prediction\input1"
target_language = 'fr'  # Target language for translation

# Function to detect the language of a text segment
def detect_language(text):
    prediction = lang_model.predict(text.strip().replace("\n", ""))
    return prediction[0][0].replace("__label__", ""), prediction[1][0]

# Process each file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_folder, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read().strip()

            if not text:
                print(f"Skipping {filename}: File is empty.")
                continue

            print(f"\nProcessing {filename}:")

            # Split text into segments (e.g., by spaces)
            segments = text.split(" ")
            translated_segments = []

            for segment in segments:
                segment = segment.strip()
                if not segment:
                    continue

                # Detect language of the segment
                detected_language, confidence = detect_language(segment)

                try:
                    # Translate segment
                    output = translation_pipeline(
                        segment, 
                        src_lang=detected_language, 
                        tgt_lang=target_language
                    )
                    translated_text = output[0]['translation_text']
                    translated_segments.append(translated_text)
                except Exception as segment_error:
                    print(f"Error translating segment: {segment}. Error: {segment_error}")
                    translated_segments.append(segment)  # Keep original if translation fails

            # Combine translated segments into the full translated text
            full_translated_text = " ".join(translated_segments)
            print(f"Original: {text}")
            print(f"Translated: {full_translated_text}\n")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
