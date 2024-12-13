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
import logging
import fasttext

# Configure logging
logging.basicConfig(
    filename="language_detection.log",
    format="%(asctime)s %(message)s",
    filemode="a",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# FastText language detection model path
fasttext_model_path = "/content/drive/MyDrive/amz12/lid.176.bin"  # Replace with your actual FastText model path

# Load the FastText model
lang_model = fasttext.load_model(fasttext_model_path)

class LanguageDetectionService:
    def __init__(self, text: str):
        """
        Initialize the language detection service.
        :param text: The text to detect the language.
        """
        self.text = text

    def detect_language(self):
        """
        Perform language detection on the input text.
        :return: Detected language.
        """
        try:
            # Detect the language
            lang_prediction = lang_model.predict(self.text)
            lang_code = lang_prediction[0][0].replace("__label__", "")
            logger.info(f"Detected language: {lang_code}")
            return lang_code
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            raise

    def main(self):
        """
        Main function to execute the language detection process.
        :return: Detected language.
        """
        return self.detect_language()


if __name__ == "__main__":
    # Example usage
    sample_text = "This is a test text to detect language."

    lang_detector = LanguageDetectionService(sample_text)
    try:
        detected_language = lang_detector.main()
        print("Detected Language:", detected_language)
    except Exception as e:
        print(f"Error during language detection: {e}")
