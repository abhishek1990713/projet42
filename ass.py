
import re

# ---------- Step 1: Normalize the input text ----------
def normalize_text(text):
    """
    Cleans the input text by fixing OCR issues like broken URLs.
    """
    # Replace multiple spaces or newlines with a single space
    text = re.sub(r'\s+', ' ', text)

    # Fix space after dot in domain (e.g., 'www. example' → 'www.example')
    text = re.sub(r'(?<=\w)\.\s+(?=\w)', '.', text)

    # Fix space between domain and path (e.g., 'example.com /path' → 'example.com/path')
    text = re.sub(r'(?<=\.\w{2,})\s+/', '/', text)

    return text.strip()


# ---------- Step 2: URL extraction ----------
def extract_urls(text):
    """
    Extracts full URLs from cleaned text using regex.
    """
    text = normalize_text(text)
    return re.findall(r'https?://(?:[\w\-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?', text)


# ---------- Step 3: Website extraction ----------
def extract_websites(text):
    """
    Extracts www-style websites (e.g., www.example.com).
    """
    text = normalize_text(text)
    return re.findall(r'\b(?:www\.)[^\s]+\.[a-zA-Z]{2,}(?:/[^\s]*)?', text)


# ---------- Step 4: Email extraction ----------
def extract_emails(text):
    """
    Extracts emails using standard regex.
    """
    return re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)


# ---------- Step 5: Final Combined Function ----------
def extract_regex_entities(text):
    """
    Extract valid emails, URLs, and websites.
    Returns a list of entity dictionaries and list of email addresses.
    """
    entities = []

    url_matches = extract_urls(text)
    website_matches = extract_websites(text)
    email_matches = extract_emails(text)

    # URLs
    for url in url_matches:
        entities.append({'label': 'URL', 'text': url})

    # Websites (skip if already captured as full URL)
    for site in website_matches:
        if site not in url_matches:
            entities.append({'label': 'Website', 'text': site})

    # Emails
    for email in email_matches:
        entities.append({'label': 'Email', 'text': email})

    return entities, email_matches
