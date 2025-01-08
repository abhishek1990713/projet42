from flask import Flask, jsonify, request
import ssl

import os
from datetime import datetime
import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Paths to models and directories
pretrained_lang_model = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
checkpoint = r"C:\CitiDev\language_prediction\m2m"
input_folder = r"C:\CitiDev\language_prediction\input"
target_language = 'en'

# Log file setup
log_file = os.path.join(input_folder, f"translation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Initialize models
lang_model = fasttext.load_model(pretrained_lang_model)
translation_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Translation pipeline
translation_pipeline = pipeline(
    'translation',
    model=translation_model,
    tokenizer=tokenizer,
    max_length=400
)

# Function to log messages
def log_message(message):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(message + '\n')
    print(message)

# Function to detect language
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
                log_message(f"Skipping {filename}: File is empty.")
                continue

            log_message(f"\nProcessing {filename}:")

            # Split text into segments
            segments = text.split("\n")
            translated_segments = []

            for segment in segments:
                segment = segment.strip()
                if not segment:
                    continue

                # Detect language
                detected_language, confidence = detect_language(segment)
                log_message(f"Segment: '{segment}' | Detected Language: {detected_language} | Confidence: {confidence}")

                try:
                    # Translate segment
                    output = translation_pipeline(
                        segment,
                        src_lang=detected_language,
                        tgt_lang=target_language
                    )
                    translated_text = output[0]['translation_text']
                    log_message(f"Translated Segment: {translated_text}")
                    translated_segments.append(translated_text)
                except Exception as segment_error:
                    log_message(f"Error translating segment: {segment}. Error: {segment_error}")
                    translated_segments.append(segment)

            # Combine translated segments
            full_translated_text = "\n".join(translated_segments)

            log_message(f"Original: {text}")
            log_message(f"Translated: {full_translated_text}")

            # Print translation to console
            print(f"\n### Translation for {filename} ###")
            print(full_translated_text)
            print("\n################################")

        except Exception as e:
            log_message(f"Error processing {filename}: {e}")
