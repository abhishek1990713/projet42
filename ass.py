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
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Translation model checkpoint
checkpoint = r"C:\CitiDev\language_prediction\m2m"

# Load translation model and tokenizer
translation_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Set up the translation pipeline
translation_pipeline = pipeline(
    'translation', 
    model=translation_model, 
    tokenizer=tokenizer, 
    max_length=400
)

# Input folder path
input_folder = r"C:\CitiDev\language_prediction\input1"

# Specify source languages for each language in the text (manually set based on input content)
source_languages = {
    "en": "English",
    "zh": "Chinese",
    "vi": "Vietnamese",
    "hi": "Hindi",
    "es": "Spanish",
    "ja": "Japanese"
}

# Target language for translation (e.g., 'fr' for French)
target_language = 'fr'

# Process each file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_folder, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.readlines()
            
            if not text:
                print(f"Skipping {filename}: File is empty.")
                continue

            print(f"\nProcessing {filename}:")
            
            for line in text:
                line = line.strip()
                if not line:
                    continue
                
                # Identify the language for each line manually (default to 'en' if not listed)
                for src_lang in source_languages:
                    if line.startswith(source_languages[src_lang]):
                        source_language = src_lang
                        break
                else:
                    source_language = "en"  # Default to English if not matched

                # Translate each line
                output = translation_pipeline(
                    line, 
                    src_lang=source_language, 
                    tgt_lang=target_language
                )
                translated_text = output[0]['translation_text']
                print(f"Original ({source_language}): {line}")
                print(f"Translated ({target_language}): {translated_text}\n")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
