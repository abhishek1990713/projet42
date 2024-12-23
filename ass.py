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

# Step 1: Load FastText model for language detection
pretrained_lang_model = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
lang_model = fasttext.load_model(pretrained_lang_model)

# Step 2: Load translation model and tokenizer
checkpoint = r"C:\CitiDev\language_prediction\m2m"
translation_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Translation pipeline
translation_pipeline = pipeline('translation', model=translation_model, tokenizer=tokenizer, max_length=400)

# Define input and output folders
input_folder = r"C:\path\to\your\input_folder"  # Folder containing .txt files
output_folder = r"C:\path\to\your\output_folder"  # Folder to save translated .txt files

os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

# Supported target languages
target_languages = ['es', 'fr', 'ru', 'ja', 'hi']

# Process each file in the folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_folder, filename)
        
        try:
            # Read the text file
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read().strip()

            if not text:
                print(f"Skipping {filename}: File is empty.")
                continue

            print(f"Processing {filename}: Original Text = {text}")

            # Detect multiple languages and their probabilities
            lang_predictions = lang_model.predict(text, k=5)
            detected_languages = lang_predictions[0]
            confidence_scores = lang_predictions[1]

            # Calculate percentage-wise contributions
            total_confidence = sum(confidence_scores)
            language_contributions = {
                lang.replace("__label__", ""): round((conf / total_confidence) * 100, 2)
                for lang, conf in zip(detected_languages, confidence_scores)
            }

            print(f"Detected Languages and Contributions: {language_contributions}")

            # Use the language with the highest confidence as the source language
            src_lang = max(language_contributions, key=language_contributions.get)

            # Translate into all target languages
            translations = {}
            for target_lang in target_languages:
                if src_lang == target_lang:
                    continue  # Skip translation if source and target languages are the same
                try:
                    output = translation_pipeline(text, src_lang=src_lang, tgt_lang=target_lang)
                    translations[target_lang] = output[0]['translation_text']
                    print(f"Translation to {target_lang}: {translations[target_lang]}")
                except Exception as e:
                    print(f"Error translating to {target_lang}: {e}")

            # Save results to a .txt file in the output folder
            output_file_path = os.path.join(output_folder, filename)
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(f"Original Text:\n{text}\n\n")
                output_file.write("Detected Languages (Percentage Contribution):\n")
                for lang, percent in language_contributions.items():
                    output_file.write(f"{lang}: {percent}%\n")
                output_file.write("\n")
                for lang, translation in translations.items():
                    output_file.write(f"Translation ({lang}):\n{translation}\n\n")

            print(f"Saved translations to {output_file_path}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("Translation completed for all files.")
