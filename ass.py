

import re
import json
from gliner import GLINER

# === Load GLiNER model ===
model_path = r"/home/ko19678/NER_gliner/model_gliner/glinerv2.5-pytorch-default-v1/gliner_model_v2.5"
model = GLINER.from_pretrained(model_path)

# === Entity Types (Expanded) ===
entity_types = [
    "person", "organization", "location", "gpe", "company", "address", "product", "bank",
    "country", "state", "website", "email", "BIC_code/Swift_code"
]

# === Email & Website Regex ===
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
WEBSITE_REGEX = r'^(https?://)?(www\.)?[\w\-]+\.[a-z]{2,}(/[\w\-./?%&=]*)?$'

def is_valid_email(text):
    return re.match(EMAIL_REGEX, text)

def is_valid_website(text):
    return re.match(WEBSITE_REGEX, text)

def is_likely_name(text):
    return bool(re.match(r'^[A-Z][a-z]+(,?\s+[A-Z][a-z]+)+$', text))

# === Text Chunking ===
def chunk_text_with_overlap(text, max_words=250, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + max_words]
        chunks.append(' '.join(chunk))
        i += max_words - overlap
    return chunks

# === Entity Extraction ===
def extract_entities(text, entity_types, threshold=0.85):
    chunks = chunk_text_with_overlap(text)
    all_entities = []
    for chunk in chunks:
        results = model.predict_entities(chunk, entity_types)
        # Only keep results above threshold
        filtered = [r for r in results if r.get("score", 1.0) >= threshold]
        all_entities.extend(filtered)
    return all_entities

# === Deduplicate & Clean Output ===
def deduplicate_entities(entities):
    seen = set()
    unique = []
    for e in entities:
        text = e["text"].strip()
        label = e["label"]
        score = round(e.get("score", 1.0), 3)

        # Reject bad email/website predictions
        if label == "email" and not is_valid_email(text):
            continue
        if label == "website" and not is_valid_website(text):
            continue
        if label == "email" and is_likely_name(text):
            continue

        key = (text.lower(), label)
        if key not in seen:
            seen.add(key)
            unique.append({
                "text": text,
                "label": label,
                "score": score
            })
    return unique

# === Extract Names from Email Headers ===
def extract_names_from_email_format(text):
    # Example: John Doe <john.doe@example.com>
    pattern = re.findall(r'([\w\s,]+)\s*<([\w\.-]+@[\w\.-]+\.\w+)>', text)
    names = [name.strip().replace(",", "") for name, _ in pattern]
    return names

# === Full Pipeline ===
def run_gliner_pipeline(input_text, threshold=0.85):
    # 1. Extract names from email formats like: "John Doe <john.doe@citi.com>"
    extracted_names = extract_names_from_email_format(input_text)

    # 2. Extract entities using model
    model_entities = extract_entities(input_text, entity_types, threshold)

    # 3. Create synthetic person entities from names (if not already found)
    for name in extracted_names:
        model_entities.append({"text": name, "label": "person", "score": 0.99})

    # 4. Filter & deduplicate
    final_entities = deduplicate_entities(model_entities)

    return final_entities

# === Example Usage ===
if __name__ == "__main__":
    text = """
    Please contact Dooling, Grayson <grayson.dooling@citi.com> for onboarding. 
    Visit our site at www.citi.com or https://citi.com/support. 
    Also loop in Sarah Davis <sarah.davis@company.org> and support@company.org.
    """

    results = run_gliner_pipeline(text, threshold=0.85)

    print(json.dumps(results, indent=2, ensure_ascii=False))

