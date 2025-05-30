import os
import json
import re
from gliner import GLINER

# Load GLiNER model
model_path = r"/home/ko19678/NER_gliner/model_gliner/glinerv2.5-pytorch-default-v1/gliner_model_v2.5"
model = GLINER.from_pretrained(model_path)

# Define entity types
entity_types = [
    "person", "organization", "location", "gpe", "company", "address",
    "product", "bank", "country", "state", "website", "email", "BIC_code/Swift_code"
]

MIN_CONFIDENCE = 0.2  # Minimum score to include GLiNER entity

# Chunk text with overlap for large documents
def chunk_text_with_overlap(text, max_words=250, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + max_words]
        chunks.append(' '.join(chunk))
        i += max_words - overlap
    return chunks

# Extract structured entities using regex
def extract_regex_entities(text):
    regex_patterns = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "website": r"https?://[^\s]+|www\.[^\s]+",
        "phone number": r"(?:(?:\+|00)[0-9]{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}",
        "BIC_code/Swift_code": r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b",
        "invoice number": r"(?:INV[- ]?)?\d{4,10}",
        "amount": r"[$€¥₹]?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
        "date": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
        "company": r"\b\w+(?:\s\w+)*(?:\sLtd\.|\sInc\.|\sLLC|\sLimited)\b"
    }

    results = []
    for label, pattern in regex_patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            results.append({
                "text": match.group().strip(),
                "label": label,
                "score": 1.0
            })
    return results

# Extract entities using GLiNER and regex
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

    # Add regex results
    regex_entities = extract_regex_entities(text)
    all_entities.extend(regex_entities)

    return all_entities

# Deduplicate by (text, label)
def deduplicate_entities(entities):
    seen = set()
    unique_entities = []
    for e in entities:
        key = (e["text"].lower(), e["label"].lower())
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
            entities = extract_entities(text, entity_types)
            deduped = deduplicate_entities(entities)
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_folder, output_filename)
            with open(output_path, "w", encoding="utf-8") as out_file:
                json.dump(deduped, out_file, indent=2, ensure_ascii=False)
            print(f"✅ Processed: {filename} → {output_filename}")

# Entry point
if __name__ == "__main__":
    input_folder = r"/home/ko19678/NER_gliner/New folder"     # Input text files
    output_folder = r"/home/ko19678/NER_gliner/New folder"    # Output JSON files
    process_folder(input_folder, output_folder)
