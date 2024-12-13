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
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.trainers import BpeTrainer

# Define your small text directly as a string
small_text = """
This is a test sentence for tokenizer training.
The tokenizer will learn from this text data.
Another example sentence to train the tokenizer.
"""

# Save this small text to a temporary file for tokenizer training
with open("temp_text.txt", "w") as file:
    file.write(small_text)

# Initialize the tokenizer
tokenizer = Tokenizer(BPE())
tokenizer.pre_tokenizer = Whitespace()

# Specify the file path of the temporary text file
files = ["temp_text.txt"]

# Initialize the trainer with desired parameters (e.g., vocab size)
trainer = BpeTrainer(vocab_size=30000, special_tokens=["<pad>", "<s>", "</s>", "<unk>"])

# Train the tokenizer
tokenizer.train(files, trainer)

# Save the trained tokenizer to a file
tokenizer.save("tokenizer.json")
print("Tokenizer saved successfully!")

# Optional: Test the tokenizer
text = "This is a test sentence."
tokens = tokenizer.encode(text)
print("Tokens:", tokens.tokens)
