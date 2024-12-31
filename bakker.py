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
    
import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import PyPDF2
import json


def translate_content(content, lang_model, translation_pipeline, target_language):
    """
    Translate the provided content into the target language.

    Args:
        content (str): The input content to translate.
        lang_model: Pretrained language detection model.
        translation_pipeline: Hugging Face translation pipeline.
        target_language (str): The target language for translation.

    Returns:
        list: List of translated segments.
    """
    segments = content.split("\n")
    translated_segments = []

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        # Detect language
        prediction = lang_model.predict(segment.replace("\n", ""))
        detected_language = prediction[0][0].replace("__label__", "")

        try:
            # Translate segment
            output = translation_pipeline(
                segment,
                src_lang=detected_language,
                tgt_lang=target_language
            )
            translated_segments.append({
                "original": segment,
                "detected_language": detected_language,
                "translated": output[0]['translation_text']
            })
        except Exception as e:
            translated_segments.append({
                "original": segment,
                "detected_language": detected_language,
                "translated": f"Error: {str(e)}"
            })

    return translated_segments


def translate_file(file_path, pretrained_lang_model, checkpoint, target_language):
    """
    Translate the content of a single file into the target language.

    Args:
        file_path (str): Path to the input file.
        pretrained_lang_model (str): Path to the FastText language detection model.
        checkpoint (str): Path to the translation model checkpoint.
        target_language (str): The target language for translation.

    Returns:
        dict: Translated content and metadata.
    """
    # Load models
    lang_model = fasttext.load_model(pretrained_lang_model)
    translation_model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)

    translation_pipeline = pipeline(
        'translation',
        model=translation_model,
        tokenizer=tokenizer,
        max_length=400
    )

    # Read file content
    _, ext = file_path.split('.')[-1].lower()
    content = ""

    if ext == "txt":
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
    elif ext == "pdf":
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                content += page.extract_text().strip() + "\n"
    elif ext == "json":
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            content = json.dumps(data, ensure_ascii=False, indent=4)
    else:
        raise ValueError("Unsupported file format. Only PDF, TXT, and JSON files are allowed.")

    # Translate content
    translated_content = translate_content(content, lang_model, translation_pipeline, target_language)

    return {
        "file_name": file_path.split("/")[-1],
        "target_language": target_language,
        "translations": translated_content
    }
