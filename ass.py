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
import logging
from enum import Enum
from huggingface_hub import hf_hub_download
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

# Configure logging
logging.basicConfig(
    filename="translation.log",
    format="%(asctime)s %(message)s",
    filemode="a",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Translation model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-1.3B")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-1.3B").to(device)

# Language codes
class LanguageCodes(Enum):
    Afrikaans = "afr_Latn"
    Amharic = "amh_Ethi"
    Arabic = "arb_Arab"
    Turkish = "tur_Latn"
    Urdu = "urd_Arab"
    Vietnamese = "vie_Latn"
    # Add more language codes as needed


class TranslationService:
    def __init__(self, text: str, target_lang: str):
        """
        Initialize the translation service.
        :param text: The text to translate.
        :param target_lang: Target language (as defined in LanguageCodes Enum).
        """
        self.text = text
        self.target_lang = target_lang

    def translate(self):
        """
        Perform translation of the input text.
        :return: Translated text.
        """
        try:
            # Validate target language
            if self.target_lang not in LanguageCodes.__members__:
                raise ValueError(f"Unsupported target language: {self.target_lang}")

            target_lang_code = LanguageCodes[self.target_lang].value

            # Prepare the translation pipeline
            translator = pipeline(
                "translation",
                model=model,
                tokenizer=tokenizer,
                src_lang="en_Latn",  # Assuming source language is English
                tgt_lang=target_lang_code,
                max_length=6000,
            )

            # Translate the text
            output = translator(self.text)
            translated_text = output[0]["translation_text"]
            logger.info("Translation successful")
            return translated_text
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise

    def main(self):
        """
        Main function to execute the translation process.
        :return: Translated text.
        """
        return self.translate()


if __name__ == "__main__":
    # Example usage
    sample_text = "This is a test text to translate."
    target_language = "Vietnamese"

    translator = TranslationService(sample_text, target_language)
    try:
        translated_output = translator.main()
        print("Translated Text:", translated_output)
    except Exception as e:
        print(f"Error during translation: {e}")
