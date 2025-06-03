import re

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'

def is_valid_email(text):
    return re.match(EMAIL_REGEX, text)

def deduplicate_entities(entities):
    seen = set()
    unique = []

    for e in entities:
        text = e["text"].strip()
        label = e["label"]
        score = round(e.get("score", 1.0), 3)

        # If labeled email but doesn't match pattern, skip
        if label == "email" and not is_valid_email(text):
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
