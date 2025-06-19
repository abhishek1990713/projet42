

def extract_regex_entities(text, ocr_results=None):
    """
    Extract valid emails, URLs, and websites from text and ocr_results.
    Attach spatial metadata from OCR blocks if available.
    """
    entities = []

    email_matches = extract_emails(text)
    name_email_pairs = extract_name_email_pairs(text)
    url_matches = extract_urls(text)
    website_matches = extract_websites(text)

    name_email_addresses = [email for _, email in name_email_pairs if is_valid_email(email)]
    remaining_emails = [e for e in email_matches if is_valid_email(e) and e not in name_email_addresses]

    def find_coordinates(matched_text):
        if not ocr_results:
            return None
        for block in ocr_results:
            if matched_text in block.get("text", ""):
                return {
                    "x": block.get("x"),
                    "y": block.get("y"),
                    "width": block.get("width"),
                    "height": block.get("height"),
                    "page": block.get("page"),
                    "start_index": text.find(matched_text),
                    "end_index": text.find(matched_text) + len(matched_text),
                    "Coordinates": []
                }
        return None

    for name, email in name_email_pairs:
        if is_valid_email(email):
            base = {
                TEXT: email,
                LABEL: "email",
                "name": name.strip()
            }
            coord = find_coordinates(email)
            if coord:
                base.update(coord)
            entities.append(base)

    for email in remaining_emails:
        base = {
            TEXT: email,
            LABEL: "email"
        }
        coord = find_coordinates(email)
        if coord:
            base.update(coord)
        entities.append(base)

    for url in url_matches:
        base = {
            TEXT: url,
            LABEL: "URL"
        }
        coord = find_coordinates(url)
        if coord:
            base.update(coord)
        entities.append(base)

    for website in website_matches:
        base = {
            TEXT: website,
            LABEL: "website"
        }
        coord = find_coordinates(website)
        if coord:
            base.update(coord)
        entities.append(base)

    return entities, email_matches

