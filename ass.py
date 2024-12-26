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

# Target language for translation (e.g., 'fr' for French)
target_language = 'fr'

# Source language (replace with the source language code of your input text)
source_language = 'en'

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

            print(f"\nProcessing {filename}: Original Text = {text}")

            # Translate the entire text
            output = translation_pipeline(
                text, 
                src_lang=source_language, 
                tgt_lang=target_language
            )
            translated_text = output[0]['translation_text']

            print(f"Translated Text ({target_language}): {translated_text}")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
