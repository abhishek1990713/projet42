def Extract_website_and_email(text, config, ocr_results, logger):
    """
    Extract only emails, websites, and URLs from OCR blocks using regex.
    Return OCR blocks with 'label' key where applicable.
    """
    try:
        extracted_blocks = []

        for block in ocr_results:
            block_text = block.get("text", "").strip()
            if not block_text:
                continue

            # Extract entities from this block's text
            entities, _ = extract_regex_entities(block_text)

            for entity in entities:
                if entity.get(TEXT) == block_text and entity.get(LABEL) in ["email", "website", "URL"]:
                    block["label"] = entity.get(LABEL)
                    extracted_blocks.append(block)
                    break  # No need to check further once matched

        logger.info(f"Found {len(extracted_blocks)} email/URL/website blocks from OCR.")
        return extracted_blocks

    except Exception as e:
        logger.error(f"Error in Extract_website_and_email: {str(e)}")
        return []

