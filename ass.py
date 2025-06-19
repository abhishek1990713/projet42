def Extract_website_and_email(text, config, ocr_results, logger):
    """
    Extract only emails, websites, and URLs from OCR blocks using regex.
    For each match, add:
      - 'label' (email / website / URL)
      - 'start_index' (start of match in block text)
      - 'end_index' (end of match in block text)
    """
    try:
        extracted_blocks = []

        for block in ocr_results:
            block_text = block.get("text", "").strip()
            if not block_text:
                continue

            # Extract regex entities from this block's text
            entities, _ = extract_regex_entities(block_text)

            for entity in entities:
                match_text = entity.get(TEXT)
                label = entity.get(LABEL)

                if label in ["email", "website", "URL"] and match_text in block_text:
                    start_index = block_text.find(match_text)
                    end_index = start_index + len(match_text)

                    block_with_label = dict(block)  # Make a copy to avoid mutating original
                    block_with_label["label"] = label
                    block_with_label["start_index"] = start_index
                    block_with_label["end_index"] = end_index

                    extracted_blocks.append(block_with_label)
                    break  # Only one match per block

        logger.info(f"Extracted {len(extracted_blocks)} email/website/URL entities with indices from OCR.")
        return extracted_blocks

    except Exception as e:
        logger.error(f"Error in Extract_website_and_email: {str(e)}")
        return []

