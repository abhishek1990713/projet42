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
import sentencepiece as spm

# Step 1: Specify model and save path

save_path = "/content/drive/MyDrive/lang"


# Step 3: Load the tokenizer from the saved path
print("\nLoading tokenizer from the saved path...")
try:
    tokenizer = AutoTokenizer.from_pretrained(save_path)
    print("Tokenizer loaded successfully!")
except Exception as e:
    print(f"Error loading tokenizer: {e}")
    exit(1)

# Step 4: Test the tokenizer
print("\nTesting the tokenizer...")
test_text = "This is a test sentence for tokenization."
tokens = tokenizer.tokenize(test_text)
input_ids = tokenizer.encode(test_text, return_tensors="pt")

print("Tokens:", tokens)
print("Input IDs:", input_ids)

# Decode back to text
decoded_text = tokenizer.decode(input_ids[0])
print("Decoded Text:", decoded_text)

# Step 5 (Optional): Use SentencePiece directly if necessary
print("\nTesting SentencePiece processor (optional)...")
try:
    sp = spm.SentencePieceProcessor()
    sp.load(f"{save_path}/sentencepiece.bpe.model")

    sp_tokens = sp.encode(test_text, out_type=str)
    print("SentencePiece Tokens:", sp_tokens)
except Exception as e:
    print(f"Error with SentencePiece: {e}")
