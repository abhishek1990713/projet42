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
    
    # Run the Flask app with SSL enabled
    app.run(host='127.0.0.1', port=8013, ssl_context=context)

# constant.pyimport fasttext
import logging
from enum import Enum
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

# Model and tokenizer paths
save_path = "/content/drive/MyDrive/amz12/models--facebook--nllb-200-1.3B"

# Load the tokenizer and model from the specified local paths
tokenizer = AutoTokenizer.from_pretrained(save_path)
model = AutoModelForSeq2SeqLM.from_pretrained(save_path).to(device)

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
    def __init__(self, text: str, src_lang: str, target_lang: str):
        """
        Initialize the translation service.
        :param text: The text to translate.
        :param src_lang: Source language code (as defined in LanguageCodes Enum).
        :param target_lang: Target language code (as defined in LanguageCodes Enum).
        """
        self.text = text
        self.src_lang = src_lang
        self.target_lang = target_lang

    def translate(self):
        """
        Perform translation of the input text.
        :return: Translated text.
        """
        try:
            # Validate source and target languages
            if self.src_lang not in LanguageCodes.__members__:
                raise ValueError(f"Unsupported source language: {self.src_lang}")
            if self.target_lang not in LanguageCodes.__members__:
                raise ValueError(f"Unsupported target language: {self.target_lang}")

            src_lang_code = LanguageCodes[self.src_lang].value
            target_lang_code = LanguageCodes[self.target_lang].value

            # Prepare the translation pipeline
            translator = pipeline(
                "translation",
                model=model,
                tokenizer=tokenizer,
                src_lang=src_lang_code,
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
    source_language = "English"  # Change to match the LanguageCodes Enum
    target_language = "Vietnamese"

    translator = TranslationService(sample_text, source_language, target_language)
    try:
        translated_output = translator.main()
        print("Translated Text:", translated_output)
    except Exception as e:
        print(f"Error during translation: {e}")
