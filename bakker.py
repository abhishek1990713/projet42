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
from tokenizers.processors import TemplateProcessing

# Step 1: Initialize a tokenizer
tokenizer = Tokenizer(BPE())

# Step 2: Set pre-tokenizer
tokenizer.pre_tokenizer = Whitespace()

# Step 3: Train the tokenizer (on your dataset)
trainer = BpeTrainer(vocab_size=30000, special_tokens=["<pad>", "<s>", "</s>", "<unk>"])
files = ["path_to_your_dataset.txt"]  # Replace with the path to your training data
tokenizer.train(files, trainer)

# Step 4: Add a post-processor (optional)
tokenizer.post_processor = TemplateProcessing(
    single="<s> $A </s>",
    pair="<s> $A </s> </s> $B </s>",
    special_tokens=[("<s>", 1), ("</s>", 2)],
)

# Step 5: Save the tokenizer
save_path = "path_to_save_tokenizer"
tokenizer.save(f"{save_path}/tokenizer.json")
print(f"Tokenizer saved to: {save_path}")

# Step 6: Load the tokenizer from the saved path
loaded_tokenizer = Tokenizer.from_file(f"{save_path}/tokenizer.json")
print("Tokenizer loaded successfully!")

# Step 7: Test the tokenizer
test_sentence = "This is a test sentence for tokenization."
output = loaded_tokenizer.encode(test_sentence)

print("Tokens:", output.tokens)
print("Input IDs:", output.ids)
decoded_text = loaded_tokenizer.decode(output.ids)
print("Decoded Text:", decoded_text)

