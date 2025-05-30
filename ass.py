


         import re
import json
from gliner import GLINER

# Load GLiNER model
model_path = r"/home/ko19678/NER_gliner/model_gliner/glinerv2.5-pytorch-default-v1/gliner_model_v2.5"
model = GLINER.from_pretrained(model_path)

# Define entity types
entity_types = [
    "person", "organization", "location", "gpe", "company", "address", "product",
    "bank", "country", "state", "website", "email", "BIC_code/Swift_code", "limited"
]

CONFIDENCE_THRESHOLD = 0.75

def chunk_text_with_overlap(text, max_words=250, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + max_words]
        chunks.append(' '.join(chunk))
        i += max_words - overlap
    return chunks

def extract_gliner_entities(text, entity_types, threshold=0.75):
    chunks = chunk_text_with_overlap(text)
    all_entities = []
    for chunk in chunks:
        entities = model.predict_entities(chunk, entity_types)
        for e in entities:
            score = round(e.get("score", 1.0), 3)
            if score >= threshold:
                all_entities.append({
                    "text": e["text"].strip(),
                    "label": e["label"],
                    "score": score
                })
    return all_entities

def extract_regex_entities(text):
    patterns = {
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "phone": r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?){1,3}\d{3,4}",
        "date": r"\b(?:\d{1,2}[/-])?(?:\d{1,2}[/-])?\d{2,4}\b",
        "invoice": r"\b(?:INV|Invoice|Bill)[-\s]?\d{3,10}\b",
        "website": r"https?://[^\s]+|www\.[^\s]+",
        "swift_code": r"\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b"
    }

    found_entities = []
    emails_found = []

    for label, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for match in matches:
            found_entities.append({
                "text": match,
                "label": label,
                "score": 1.0
            })
            if label == "email":
                emails_found.append(match)
    return found_entities, emails_found

def deduplicate_entities(entities):
    seen = set()
    unique = []
    for e in entities:
        key = (e["text"].lower(), e["label"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique

def extract_names_from_emails(email_list):
    names = []
    for email in email_list:
        local_part = email.split('@')[0]
        name = re.sub(r'[\._\-]+', ' ', local_part).strip()
        if name:
            names.append(name)
    return names

def classify_names_with_gliner(names):
    result = []
    for name in names:
        entities = model.predict_entities(name, entity_types)
        for e in entities:
            score = round(e.get("score", 1.0), 3)
            if score >= CONFIDENCE_THRESHOLD:
                result.append({
                    "text": e["text"].strip(),
                    "label": e["label"],
                    "score": score
                })
    return result

def process_text(text):
    gliner_entities = extract_gliner_entities(text, entity_types, threshold=CONFIDENCE_THRESHOLD)
    regex_entities, email_list = extract_regex_entities(text)

    # Extract names from emails and classify them
    email_names = extract_names_from_emails(email_list)
    email_name_entities = classify_names_with_gliner(email_names)

    combined = gliner_entities + regex_entities + email_name_entities
    results = deduplicate_entities(combined)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return results

# Example usage
if __name__ == "__main__":
    text = """
    John Doe <john.doe@example.com> is the CTO of FutureTech Ltd.
    The invoice number is INV-87654321 dated 12/04/2023 for $2,345.67.
    Visit our website at www.futuretech.com or call +1-800-555-1234.
    Swift Code: CHASUS33XXX
    """
    process_text(text)
       
