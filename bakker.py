from flask import Flask, jsonify, request
import ssl

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello, client! Connection is secure."})

if __name__ == '__main__':
    # SSL context configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.verify_mode = ssl.CERT_REQUIRED  # Require client certificate verification
    context.load_cert_chain(certfile='certificate.cer', keyfile='private.key')
    context.load_verify_locations(cafile='CA.pem')  # Load the CA certificate for client verification
    
import os
import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from datetime import datetime

# Paths and configurations
pretrained_lang_model = r"C:\CitiDev\language_prediction\amz12\lid.176.bin"
lang_model = fasttext.load_model(pretrained_lang_model)

checkpoint = r"C:\CitiDev\language_prediction\m2m"
translation_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

translation_pipeline = pipeline(
    'translation',
    model=translation_model,
    tokenizer=tokenizer,
    max_length=400
)

input_folder = r"C:\CitiDev\language_prediction\input1"
output_folder = r"C:\CitiDev\language_prediction\output"
target_language = 'fr'  # Target language for translation

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Logging setup
log_file = os.path.join(output_folder, f"translation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

def log_message(message):
    """Log a message to the console and log file."""
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(message + '\n')
    print(message)

# Function to detect language
def detect_language(text):
    prediction = lang_model.predict(text.strip().replace("\n", ""))
    return prediction[0][0].replace("__label__", ""), prediction[1][0]

# Processing files
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_translated.txt")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read().strip()

            if not text:
                log_message(f"Skipping {filename}: File is empty.")
                continue

            log_message(f"\nProcessing {filename}:")

            # Split text into segments
            segments = text.split(" ")
            translated_segments = []

            for segment in segments:
                segment = segment.strip()
                if not segment:
                    continue

                # Detect language of the segment
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
                    translated_segments.append(segment)  # Keep original if translation fails

            # Combine translated segments into full text
            full_translated_text = " ".join(translated_segments)
            log_message(f"Original: {text}")
            log_message(f"Translated: {full_translated_text}")

            # Save the translation to a file
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(full_translated_text)

            log_message(f"Translation saved to: {output_file_path}\n")

        except Exception as e:
            log_message(f"Error processing {filename}: {e}")

