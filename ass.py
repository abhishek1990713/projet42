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


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index4.html')


@app.route('/predict', methods=['GET'])
def Upload():
    if request.method == 'GET':
        # print(request.json['file'])


        r = sr.Recognizer()

        sound = AudioSegment.from_wav("inp/splite.wav")

        audio_chunks = split_on_silence(sound, min_silence_len=1000, silence_thresh=sound.dBFS - 14, keep_silence=500)
        whole_text = ""
        textMap = {}
        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join('InputFiles', f"speech_chunk{i}.wav")
            print("Exporting file", output_file)
            result = chunk.export(output_file, format="wav")




        # os.remove("inp/splite.wav")
        return str(result)

    # return str(result)
    return None
import os
import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import pandas as pd

# Step 1: Load FastText model for language detection
pretrained_lang_model = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
lang_model = fasttext.load_model(pretrained_lang_model)

# Step 2: Load translation model and tokenizer
checkpoint = r"C:\CitiDev\language_prediction\m2m"
translation_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

translation_pipeline = pipeline('translation', model=translation_model, tokenizer=tokenizer, max_length=400)

# Step 3: Define folder and output Excel file paths
input_folder = r"C:\path\to\your\folder"  # Folder containing .txt files
output_excel = r"C:\path\to\output.xlsx"

# Step 4: Initialize result list
results = []

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

            # Debug: Print the original text
            print(f"Processing {filename}: Original Text = {text}")

            # Step 5: Language detection
            lang_prediction = lang_model.predict(text)
            detected_language = lang_prediction[0][0].replace("__label__", "")
            confidence_score_lang = lang_prediction[1][0]

            # Debug: Print detected language
            print(f"Detected Language: {detected_language} (Confidence: {confidence_score_lang})")

            # Skip files if the detected language is not supported
            if detected_language not in target_languages:
                print(f"Skipping {filename}: Unsupported language detected ({detected_language})")
                continue

            # Translate the text into all target languages
            translations = {}
            for target_lang in target_languages:
                output = translation_pipeline(text, src_lang=detected_language, tgt_lang=target_lang)
                translations[target_lang] = output[0]['translation_text']

                # Debug: Print translations
                print(f"Translation to {target_lang}: {translations[target_lang]}")
            
            # Save results
            results.append({
                'File Name': filename,
                'Original Text': text,
                'Detected Language Code': detected_language,
                'Confidence Score (Detection)': confidence_score_lang,
                'Translation (es)': translations.get('es', ''),
                'Translation (fr)': translations.get('fr', ''),
                'Translation (ru)': translations.get('ru', ''),
                'Translation (ja)': translations.get('ja', ''),
                'Translation (hi)': translations.get('hi', '')
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Step 6: Save results to an Excel file
if results:
    df = pd.DataFrame(results)
    df.to_excel(output_excel, index=False)  # Removed `encoding` argument
    print(f"Translation completed. Results saved to {output_excel}")
else:
    print("No results to save. Ensure the input folder contains valid .txt files with supported languages.")
