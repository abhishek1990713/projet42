import re

# ---------- Step 1: Normalize text ----------
def normalize_text(text):
    """
    Cleans the input text by fixing OCR issues like broken URLs.
    """
    text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces/newlines
    text = re.sub(r'(?<=\w)\.\s+(?=\w)', '.', text)  # Fix 'www. example'
    text = re.sub(r'(?<=\.\w{2,})\s+/', '/', text)  # Fix 'example.com /path'
    return text.strip()


# ---------- Step 2: Extract URLs ----------
def extract_urls(text):
    text = normalize_text(text)
    return re.findall(r'https?://(?:[\w\-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?', text)


# ---------- Step 3: Extract Websites ----------
def extract_websites(text):
    text = normalize_text(text)
    return re.findall(r'\b(?:www\.)[^\s]+\.[a-zA-Z]{2,}(?:/[^\s]*)?', text)


# ---------- Step 4: Extract Emails ----------
def extract_emails(text):
    return re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)


# ---------- Step 5: Detect garbage lines ----------
def is_garbage_line(line):
    return re.fullmatch(r'[\W_]{3,}', line.strip()) is not None


# ---------- Step 6: Convert to Paragraph ----------
def clean_to_paragraph(text):
    """
    Removes noisy lines and groups valid text into a clean paragraph.
    """
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty or garbage lines
        if not line or is_garbage_line(line):
            continue

        # Skip lines like "FIELD: *********"
        if re.match(r'^.*?:\s*[\W_]{3,}$', line):
            continue

        cleaned_lines.append(line)

    paragraph = ' '.join(cleaned_lines)
    paragraph = re.sub(r'\s{2,}', ' ', paragraph)
    return paragraph.strip()


# ---------- Step 7: Master Function ----------
def extract_regex_entities(text):
    """
    Extract emails, URLs, websites from cleaned text + convert to paragraph.
    Returns:
        entities: list of dictionaries
        emails: list of strings
        paragraph: cleaned paragraph text
    """
    paragraph = clean_to_paragraph(text)

    url_matches = extract_urls(paragraph)
    website_matches = extract_websites(paragraph)
    email_matches = extract_emails(paragraph)

    entities = []

    for url in url_matches:
        entities.append({'label': 'URL', 'text': url})

    for site in website_matches:
        if site not in url_matches:
            entities.append({'label': 'Website', 'text': site})

    for email in email_matches:
        entities.append({'label': 'Email', 'text': email})

    return entities, email_matches, paragraph

