def extract_regex_entities(text, ocr_results=None):
    """
    Extract valid emails, URLs, and websites.
    If OCR blocks are provided, attach spatial metadata dynamically.
    Returns:
        entities: List of entity dicts with full metadata
        email_matches: List of raw email strings
    """
    entities = []

    email_matches = extract_emails(text)
    name_email_pairs = extract_name_email_pairs(text)
    url_matches = extract_urls(text)
    website_matches = extract_websites(text)

    name_email_addresses = [email for _, email in name_email_pairs if is_valid_email(email)]
    remaining_emails = [e for e in email_matches if is_valid_email(e) and e not in name_email_addresses]

    def find_block_data(match_text):
        """
        Find corresponding OCR block data for a given matched text.
        """
        if not ocr_results:
            return {}
        for block in ocr_results:
            block_text = block.get("text", "")
            if match_text in block_text:
                return {
                    "page": block.get("page"),
                    "x": block.get("x"),
                    "y": block.get("y"),
                    "width": block.get("width"),
                    "height": block.get("height"),
                    "start_index": text.find(match_text),
                    "end_index": text.find(match_text) + len(match_text),
                    "Coordinates": block.get("Coordinates", [])
                }
        return {
            "page": None,
            "x": None,
            "y": None,
            "width": None,
            "height": None,
            "start_index": text.find(match_text),
            "end_index": text.find(match_text) + len(match_text),
            "Coordinates": []
        }

    # Handle name-email pairs
    for name, email in name_email_pairs:
        if is_valid_email(email):
            entity = {
                TEXT: email,
                LABEL: "email",
                "name": name.strip()
            }
            entity.update(find_block_data(email))
            entities.append(entity)

    # Handle remaining emails
    for email in remaining_emails:
        entity = {
            TEXT: email,
            LABEL: "email"
        }
        entity.update(find_block_data(email))
        entities.append(entity)

    # Handle URLs
    for url in url_matches:
        entity = {
            TEXT: url,
            LABEL: "URL"
        }
        entity.update(find_block_data(url))
        entities.append(entity)

    # Handle websites
    for website in website_matches:
        entity = {
            TEXT: website,
            LABEL: "website"
        }
        entity.update(find_block_data(website))
        entities.append(entity)

    return entities, email_matches
