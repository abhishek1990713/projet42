from flask import Flask, jsonify, request
import ssl

import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from fasttext import load_model

# Load the pre-trained language detection model
pretrained_lang_model_path = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
lang_model = load_model(pretrained_lang_model_path)

# Load the translation model and tokenizer
checkpoint = r"C:\CitiDev\language_prediction\m2m"
translation_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Create a translation pipeline
translation_pipeline = pipeline(
    "translation",
    model=translation_model,
    tokenizer=tokenizer,
    max_length=100
)


def detect_language(text):
    """Detect the language of a given text."""
    prediction = lang_model.predict(text.strip().replace("\n", ""))
    return prediction[0][0].replace("__label_", ""), prediction[1][0]


# Process one file at a time
def process_file(file_path):
    """Process a single text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read().strip()

        if not text:
            print("The file is empty.")
            return

        print(f"Original Text:\n{text}\n")

        segments = text.split("\n")  # Split text into segments by lines
        translated_segments = []

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            detected_language, confidence = detect_language(segment)

            try:
                output = translation_pipeline(
                    segment,
                    src_lang=detected_language,
                    tgt_lang='en'  # Target language is English
                )
                translated_text = output[0]['translation_text']
                translated_segments.append(translated_text)
            except Exception:
                translated_segments.append(segment)

        full_translated_text = "\n".join(translated_segments)
        print(f"Translated Text:\n{full_translated_text}\n")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage: Provide the file path to process
file_path = r"C:\CitiDev\language_prediction\input\example.txt"  # Replace with your file path
process_file(file_path)
