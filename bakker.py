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
from transformers import AutoTokenizer

# Specify the save path
save_path = "/content/drive/MyDrive/amz12/models--facebook--nllb-200-1.3B"


print("Loading tokenizer from the saved path...")
local_tokenizer = AutoTokenizer.from_pretrained(save_path)
print("Tokenizer loaded successfully!")

# Step 3: Test the tokenizer
# Input text for testing
test_text = "This is a test sentence for tokenization."

# Tokenize the text
tokens = local_tokenizer.tokenize(test_text)
print("Tokens:", tokens)

# Convert tokens to input IDs
input_ids = local_tokenizer.encode(test_text, return_tensors="pt")
print("Input IDs:", input_ids)

# Decode the IDs back to text
decoded_text = local_tokenizer.decode(input_ids[0], skip_special_tokens=True)
print("Decoded text:", decoded_text)
