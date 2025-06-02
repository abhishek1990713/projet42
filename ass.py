

import os
import re
import json
from gliner import GLINER

# Load GLiNER model
model_path = "/home/ko19678/NER_gliner/model_gliner/glinerv2.5-pytorch-default-v1/gliner_model_v2.5"
model = GLINER.from_pretrained(model_path)

# Define entity types
entity_types = [
    "person", "organization", "location", "gpe", "company", "address",
    "product", "bank", "country", "state", "website", "email", "BIC_code/Swift_code"
]

CONFIDENCE_THRESHOLD = 0.6

# Chunk text for processing

def chunk_text_with_overlap(text, max_words=250, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + max_words]
        chunks.append(' '.join(chunk))
        i += max_words - overlap
    return chunks

# Predict entities using GLiNER

def extract_gliner_entities(text, entity_types, threshold=0.6):
    chunks = chunk_text_with_overlap(text)
    all_entities = []
    for chunk in chunks:
        entities = model.predict_entities(chunk, entity_types)
        for e in entities:
            if e.get("score", 1.0) >= threshold:
                all_entities.append(e)
    return all_entities

# Regex-based entity extraction

def extract_regex_entities(text):
    entities = []
    email_pattern = r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}"
    email_matches = re.findall(email_pattern, text)
    for email in email_matches:
        entities.append({"text": email, "label": "email", "score": 1.0})
    return entities, email_matches

# Deduplicate by text and label

def deduplicate_entities(entities):
    seen = set()
    unique = []
    for e in entities:
        key = (e["text"].strip().lower(), e["label"])
        if key not in seen:
            seen.add(key)
            unique.append({
                "text": e["text"].strip(),
                "label": e["label"],
                "score": round(e.get("score", 1.0), 3)
            })
    return unique

# Extract display name and email pair

def extract_name_email_pairs(text):
    pattern = r'([\w\s,\.\"\']+)<([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,})>'
    matches = re.findall(pattern, text)
    return [(name.replace(',', '').strip().strip('"'), email) for name, email in matches]

# Classify extracted names using GLiNER

def classify_names_with_gliner(names):
    results = []
    for name in names:
        entities = model.predict_entities(name, ["person"])
        for e in entities:
            if e.get("score", 1.0) >= CONFIDENCE_THRESHOLD:
                results.append(e)
    return results

# Extract names from emails (e.g., john.doe@example.com -> John Doe)

def extract_names_from_emails(email_list):
    names = []
    for email in email_list:
        prefix = email.split('@')[0]
        clean = re.sub(r'[._-]', ' ', prefix).title()
        names.append(clean)
    return names

# Process a single text input

def process_text(text):
    gliner_entities = extract_gliner_entities(text, entity_types, threshold=CONFIDENCE_THRESHOLD)
    regex_entities, email_list = extract_regex_entities(text)

    # Extract names from patterns like: John Doe <john.doe@example.com>
    name_email_pairs = extract_name_email_pairs(text)
    display_names = [name for name, _ in name_email_pairs]

    # Classify display names and names from email prefix
    display_name_entities = classify_names_with_gliner(display_names)
    email_name_entities = classify_names_with_gliner(extract_names_from_emails(email_list))

    all = gliner_entities + regex_entities + display_name_entities + email_name_entities
    deduped = deduplicate_entities(all)

    print(json.dumps(deduped, indent=2, ensure_ascii=False))
    return deduped

# Example usage
if __name__ == "__main__":
    text = """
    Please contact Dooling, Grayson <grayson.dooling@citi.com> or visit www.citi.com.
    This invoice is from CitiBank Limited and the amount is $2,300.00.
    """
    process_text(text)

       
