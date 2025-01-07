from flask import Flask, jsonify, request
import ssl

import os
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from fasttext import load_model
from PyPDF2 import PdfReader

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

def process_txt_file(input_file, target_language):
    """Process .txt file and return translation in JSON format."""
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read().strip()

        if not text:
            return {"error": "Input file is empty."}

        segments = text.split("\n")
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
                translated_text = segment

            results.append({
                "original_text": segment,
                "detected_language": detected_language,
                "confidence": confidence,
                "translated_text": translated_text
            })

        return results

    except Exception as e:
        return {"error": str(e)}

def process_pdf_file(input_file, target_language):
    """Process .pdf file and return translation in JSON format."""
    try:
        reader = PdfReader(input_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        if not text.strip():
            return {"error": "Input PDF file is empty or could not be processed."}

        segments = text.split("\n")
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
                translated_text = segment

            results.append({
                "original_text": segment,
                "detected_language": detected_language,
                "confidence": confidence,
                "translated_text": translated_text
            })

        return results

    except Exception as e:
        return {"error": str(e)}

def process_json_file(input_file, target_language):
    """Process .json file and return translation in JSON format."""
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if not data:
            return {"error": "Input JSON file is empty."}

        results = []

        for item in data:
            segment = item.get('text', '').strip()
            if not segment:
                continue

            detected_language, confidence = lang_model.predict(segment)
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
                translated_text = segment

            results.append({
                "original_text": segment,
                "detected_language": detected_language,
                "confidence": confidence,
                "translated_text": translated_text
            })

        return results

    except Exception as e:
        return {"error": str(e)}

def process_file(input_file, target_language):
    """Main function to process the given file based on its format and target language."""
    file_extension = os.path.splitext(input_file)[1].lower()

    if file_extension == '.txt':
        return process_txt_file(input_file, target_language)
    elif file_extension == '.pdf':
        return process_pdf_file(input_file, target_language)
    elif file_extension == '.json':
        return process_json_file(input_file, target_language)
    else:
        return {"error": "Unsupported file format."}

# Example Usage
input_file = r"C:\CitiDev\language_prediction\input\input.txt"  # Specify the input file path
target_language = 'en'  # Specify the target language

result = process_file(input_file, target_language)

# Display the result
print(json.dumps(result, ensure_ascii=False, indent=4))
