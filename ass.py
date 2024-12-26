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

# Default source language (assume most of the text is in one language if unsure)
default_source_language = 'en'

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
            
            # Split the text into sentences or segments
            segments = text.split("\n")  # Split by lines
            translated_segments = []

            for segment in segments:
                segment = segment.strip()
                if not segment:
                    continue
                
                try:
                    # Translate each segment
                    output = translation_pipeline(
                        segment, 
                        src_lang=default_source_language, 
                        tgt_lang=target_language
                    )
                    translated_text = output[0]['translation_text']
                    translated_segments.append(translated_text)

                    print(f"Original: {segment}")
                    print(f"Translated: {translated_text}\n")
                except Exception as segment_error:
                    print(f"Error translating segment: {segment}. Error: {segment_error}")

            # Combine translated segments into the full translated text
            full_translated_text = "\n".join(translated_segments)
            print(f"\nFull Translated Text ({target_language}):\n{full_translated_text}\n")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
