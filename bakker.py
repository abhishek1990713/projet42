from flask import Flask, jsonify, request
import ssl

import os
import json
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

# Define the target language
target_language = 'en'


def process_file(input_file):
    """
    Process the input file and return the translation result in JSON format.
    :param input_file: Path to the input text file.
    :return: List of dictionaries containing translation results in JSON format.
    """
    if not os.path.exists(input_file):
        return {"error": f"Input file does not exist: {input_file}"}

    try:
        # Read the input text file
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read().strip()

        if not text:
            return {"error": "Input file is empty."}

        segments = text.split("\n")  # Split text into segments by lines
        results = []

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            detected_language, confidence = lang_model.predict(segment.strip().replace("\n", ""))
            detected_language = detected_language[0].replace("__label_", "")
            confidence = confidence[0]

            try:
                output = translation_pipeline(
                    segment,
                    src_lang=detected_language,
                    tgt_lang=target_language
                )
                translated_text = output[0]['translation_text']
            except Exception:
                translated_text = segment  # Keep original text if translation fails

            results.append({
                "original_text": segment,
                "detected_language": detected_language,
                "confidence": confidence,
                "translated_text": translated_text
            })

        return results

    except Exception as e:
        return {"error": str(e)}


# Example Usage
input_file = r"C:\CitiDev\language_prediction\input\input.txt"  # Specify the input file
result = process_file(input_file)

# Display the result
print(json.dumps(result, ensure_ascii=False, indent=4))
