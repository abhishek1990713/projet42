

def extract_regex_entities(text, ocr_results=None):
    """
    Extract valid emails, URLs, and websites using regex.
    Attach spatial metadata from OCR blocks where possible, like filter_entities does.
    """
    def find_spatial_metadata(match_text):
        """
        Search ocr_results for a block containing match_text and return spatial metadata.
        """
        metadata = {
            "page": None,
            "x": None,
            "y": None,
            "width": None,
            "height": None,
            "start_index": text.find(match_text),
            "end_index": text.find(match_text) + len(match_text),
            "Coordinates": []
        }
        if not ocr_results:
            return metadata
        
        for block in ocr_results:
            block_text = block.get("text", "")
            if match_text in block_text:
                metadata.update({
                    "page": block.get("page"),
                    "x": block.get("x"),
                    "y": block.get("y"),
                    "width": block.get("width"),
                    "height": block.get("height"),
                    "Coordinates": block.get("Coordinates", [])
                })
                break
        return metadata

    entities = []

    # Extract patterns
    email_matches = extract_emails(text)
    name_email_pairs = extract_name_email_pairs(text)
    url_matches = extract_urls(text)
    website_matches = extract_websites(text)

    # Split valid and duplicate emails
    name_email_addresses = [email for _, email in name_email_pairs if is_valid_email(email)]
    remaining_emails = [e for e in email_matches if is_valid_email(e) and e not in name_email_addresses]

    # Process name-email pairs
    for name, email in name_email_pairs:
        if is_valid_email(email):
            entity = {
                "text": email,
                "label": "email",
                "name": name.strip()
            }
            entity.update(find_spatial_metadata(email))
            entities.append(entity)

    # Process remaining email matches
    for email in remaining_emails:
        entity = {
            "text": email,
            "label": "email"
        }
        entity.update(find_spatial_metadata(email))
        entities.append(entity)

    # Process URL matches
    for url in url_matches:
        entity = {
            "text": url,
            "label": "URL"
        }
        entity.update(find_spatial_metadata(url))
        entities.append(entity)

    # Process website matches
    for website in website_matches:
        entity = {
            "text": website,
            "label": "website"
        }
        entity.update(find_spatial_metadata(website))
        entities.append(entity)

    return entities, email_matches
