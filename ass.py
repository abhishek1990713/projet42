
def Extract_website_and_email(text, config, ocr_results, logger):
    """
    Extract emails, URLs, and websites from the full text (including OCR).
    Adds label, start_index, and end_index (w.r.t. full text) to OCR blocks that match.

    Returns:
        List of OCR blocks with 'label', 'start_index', 'end_index'.
    """
    try:
        # Merge OCR into full text if not already present
        if ocr_results:
            ocr_text = " ".join([block.get("text", "") for block in ocr_results])
            text += " " + ocr_text

        # Extract entities from full text
        entities, _ = extract_regex_entities(text)
        valid_labels = {"email", "website", "URL"}
        filtered_entities = [ent for ent in entities if ent.get(LABEL) in valid_labels]

        labeled_blocks = []

        for ent in filtered_entities:
            value = ent.get(TEXT)
            label = ent.get(LABEL)

            # Use regex search to find exact match and index
            match = re.search(re.escape(value), text)
            if not match:
                continue  # skip if not found

            start_idx = match.start()
            end_idx = match.end()

            # Now map it to one of the OCR blocks
            for block in ocr_results:
                block_text = block.get("text", "").strip()
                if not block_text or value not in block_text:
                    continue

                block_with_label = dict(block)
                block_with_label["label"] = label
                block_with_label["start_index"] = start_idx
                block_with_label["end_index"] = end_idx

                labeled_blocks.append(block_with_label)
                break  # only one block per match

        logger.info(f"Extracted {len(labeled_blocks)} labeled entities from OCR blocks.")
        return labeled_blocks

    except Exception as e:
        logger.error(f"Error in Extract_website_and_email: {str(e)}")
        return []
