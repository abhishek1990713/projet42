

import os
import json
from gliner import GLINER

# Load GLiNER model
model_path = r"/home/ko19678/NER_gliner/model_gliner/glinerv2.5-pytorch-default-v1/gliner_model_v2.5"
model = GLINER.from_pretrained(model_path)

# Define entity types
entity_types = [
    "person", "organization", "company", "business", "corporation", "institute", "limited company",
    "LLC", "Inc", "Ltd", "Limited", "location", "city", "country", "state", "province", "region",
    "gpe", "address", "postal code", "zip code", "email", "website", "URL", "phone number", "fax number",
    "bank", "account number", "BIC_code/Swift_code", "IBAN", "transaction id", "invoice number",
    "amount", "currency", "product", "service", "item", "brand", "date", "datetime", 
    "document number", "registration number", "tax ID"
]

# Optional: set minimum score threshold
MIN_CONFIDENCE = 0.0  # Set to 0.85 to filter low-confidence entities

# Chunking function
def chunk_text_with_overlap(text, max_words=250, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + max_words]
        chunks.append(' '.join(chunk))
        i += max_words - overlap
    return chunks

# Entity extraction with confidence filtering
def extract_entities(text, entity_types):
    chunks = chunk_text_with_overlap(text)
    all_entities = []
    for chunk in chunks:
        entities = model.predict_entities(chunk, entity_types)
        for e in entities:
            if e.get("score", 1.0) >= MIN_CONFIDENCE:
                all_entities.append({
                    "text": e["text"].strip(),
                    "label": e["label"],
                    "score": round(e.get("score", 1.0), 4)
                })
    return all_entities

# Deduplicate entities based on text + label
def deduplicate_entities(entities):
    seen = set()
    unique_entities = []
    for e in entities:
        key = (e["text"].strip().lower(), e["label"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)
    return unique_entities

# Process all .txt files in input folder
def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(input_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            print(f"\n📄 Processing: {filename}")
            entities = extract_entities(text, entity_types)
            deduped = deduplicate_entities(entities)
            for e in deduped:
                print(f" → {e['text']} ({e['label']}) - Score: {e['score']}")
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_folder, output_filename)
            with open(output_path, "w", encoding="utf-8") as out_file:
                json.dump(deduped, out_file, indent=2, ensure_ascii=False)
            print(f"✅ Saved: {output_filename}")

# Main runner
if __name__ == "__main__":
    input_folder = r"/home/ko19678/NER_gliner/New folder"
    output_folder = r"/home/ko19678/NER_gliner/New folder"
    process_folder(input_folder, output_folder)
