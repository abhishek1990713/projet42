def is_likely_name(text):
    """Check if a string looks like a name instead of an email."""
    return bool(re.match(r'^[A-Z][a-z]+(,?\\s+[A-Z][a-z]+)+$', text))

def deduplicate_entities(entities):
    seen = set()
    unique = []
    for e in entities:
        text = e["text"].strip()
        label = e["label"]
        score = round(e.get("score", 1.0), 3)

        # Skip if misclassified name as email
        if label == "email" and is_likely_name(text) and not re.search(r'@', text):
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


       
