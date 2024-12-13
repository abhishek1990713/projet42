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
from transformers import AutoTokenizer

# Load tokenizer from saved path
save_path = "/content/drive/MyDrive/lang/tokenizer"
tokenizer = AutoTokenizer.from_pretrained(save_path)

print("Tokenizer loaded successfully!")
text = "This is a test sentence for tokenization."
tokens = tokenizer.tokenize(text)
input_ids = tokenizer.encode(text, return_tensors="pt")
print("Tokens:", tokens)
print("Input IDs:", input_ids)
decoded_text = tokenizer.decode(input_ids[0])
print("Decoded Text:", decoded_text)
