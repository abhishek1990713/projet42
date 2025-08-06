import re

# Updated normalize_text to handle "https://www. boeing..." issue
def normalize_text(text):
    """
    Cleans the input text by fixing common OCR issues, especially broken URLs.
    """
    # Replace newlines and multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)

    # Fix space after "www." and after protocol
    text = re.sub(r'(https?://)\s+', r'\1', text)                  # e.g., "https:// boeing.com"
    text = re.sub(r'www\.\s+', 'www.', text)                       # e.g., "www. boeing" → "www.boeing"
    text = re.sub(r'(?<=\w)\.\s+(?=\w)', '.', text)                # e.g., "boeing. com" → "boeing.com"
    text = re.sub(r'(?<=\.\w{2,})\s+/', '/', text)                 # e.g., ".com /path" → ".com/path"
    
    return text.strip()


def extract_urls(text):
    """
    Extract full URLs using robust regex after normalization.
    """
    text = normalize_text(text)
    return re.findall(r'https?://(?:[\w\-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?', text)


def extract_websites(text):
    """
    Extract www-based websites (normalized).
    """
    text = normalize_text(text)
    return re.findall(r'\bwww\.[^\s]+\.[a-zA-Z]{2,}(?:/[^\s]*)?', text)


def extract_emails(text):
    return re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)


def extract_regex_entities(text):
    """
    Extract valid emails, URLs, and websites.
    Returns a list of entity dictionaries and email list.
    """
    entities = []

    url_matches = extract_urls(text)
    website_matches = extract_websites(text)
    email_matches = extract_emails(text)

    for url in url_matches:
        entities.append({'label': 'URL', 'text': url})

    for site in website_matches:
        if site not in url_matches:
            entities.append({'label': 'Website', 'text': site})

    for email in email_matches:
        entities.append({'label': 'Email', 'text': email})

    return entities, email_matches

