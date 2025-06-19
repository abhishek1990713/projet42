def Extract_website_and_email(text, config, ocr_results, logger):
    """
    Extract emails, websites, and URLs from OCR block text using regex.
    For each match, append:
      - 'label': type of entity (email / website / URL)
      - 'start_index': character index of match start in block text
      - 'end_index': character index of match end in block text
    """
    try:
        extracted_blocks = []

        email_pattern = r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}"
        website_pattern = r'\b(?:www\.)[^\s]+\.[a-zA-Z]{2,}\b'
        url_pattern = r'https?://[^\s]+'

        for block in ocr_results:
            block_text = block.get("text", "").strip()
            if not block_text:
                continue

            # Email
            for match in re.finditer(email_pattern, block_text):
                email = match.group()
                if is_valid_email(email):
                    block_with_label = dict(block)
                    block_with_label.update({
                        "label": "email",
                        "start_index": match.start(),
                        "end_index": match.end()
                    })
                    extracted_blocks.append(block_with_label)
                    break  # one match per block

            # Website
            for match in re.finditer(website_pattern, block_text):
                website = match.group()
                block_with_label = dict(block)
                block_with_label.update({
                    "label": "website",
                    "start_index": match.start(),
                    "end_index": match.end()
                })
                extracted_blocks.append(block_with_label)
                break

            # URL
            for match in re.finditer(url_pattern, block_text):
                url = match.group()
                block_with_label = dict(block)
                block_with_label.update({
                    "label": "URL",
                    "start_index": match.start(),
                    "end_index": match.end()
                })
                extracted_blocks.append(block_with_label)
                break

        logger.info(f"Extracted {len(extracted_blocks)} labeled OCR blocks with index positions.")
        return extracted_blocks

    except Exception as e:
        logger.error(f"Error in Extract_website_and_email: {str(e)}")
        return []
