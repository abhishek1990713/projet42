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
