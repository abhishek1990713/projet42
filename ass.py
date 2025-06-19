def Extract_website_and_email(text, config, ocr_results, logger):
    """
    Extract emails and website URLs from OCR blocks using regex, and attach labels to each block.

    Returns:
        List of OCR blocks with 'label' key added where applicable.
    """
    try:
        labeled_blocks = []

        for block in ocr_results:
            block_text = block.get("text", "")
            if not block_text.strip():
                continue

            # Run regex-based entity extraction on individual text
            entities, _ = extract_regex_entities(block_text)

            # Match the original text to entity predictions
            matched = False
            for entity in entities:
                if entity.get(TEXT) == block_text:
                    block["label"] = entity.get(LABEL)
                    labeled_blocks.append(block)
                    matched = True
                    break

            if not matched:
                # Not a matchable entity, optionally include or skip
                labeled_blocks.append(block)

        logger.info(f"Labeled {sum(1 for b in labeled_blocks if 'label' in b)} blocks from OCR results.")
        return labeled_blocks

    except Exception as e:
        logger.error(f"Error in labeling OCR results with website/email: {str(e)}")
        return []

