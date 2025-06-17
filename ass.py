
def is_valid_email(text):
    """
    Check if the email address is valid using regex.
    """
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(email_regex, text)


def extract_urls(text):
    """
    Extract full URLs (http/https).
    """
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)


def extract_regex_entities(text):
    """
    Extract valid emails (from text and name-email pairs), URLs, and websites.
    Returns a list of entity dictionaries and email list.
    """
    entities = []

    email_matches = extract_emails(text)
    name_email_pairs = extract_name_email_pairs(text)
    url_matches = extract_urls(text)
    website_matches = extract_websites(text)

    name_email_addresses = [email for _, email in name_email_pairs if is_valid_email(email)]
    remaining_emails = [e for e in email_matches if is_valid_email(e) and e not in name_email_addresses]

    for name, email in name_email_pairs:
        if is_valid_email(email):
            entities.append({
                TEXT: email,
                LABEL: "email",
                "name": name.strip(),
                "score": 1.0
            })

    for email in remaining_emails:
        entities.append({
            TEXT: email,
            LABEL: "email",
            "score": 1.0
        })

    for url in url_matches:
        entities.append({
            TEXT: url,
            LABEL: "URL",
            "score": 1.0
        })

    for website in website_matches:
        entities.append({
            TEXT: website,
            LABEL: "website",
            "score": 1.0
        })

    return entities, email_matches

