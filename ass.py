def post_Screening(entities, text, ancillary_entities, ocr_results, config, logger):
    """
    Final post-processing to combine context-filtered and regex-based domain entities,
    with proper validation for email, website, and URL.
    """
    # Step 1: Context-aware filtering
    filtered_entities = filter_entities(text, entities, config, logger)

    # Step 2: Regex-based entity extraction
    domain_entities, _ = extract_regex_entities(text)

    # Step 3: Combine all entities
    combined_entities = filtered_entities + domain_entities

    # Step 4: Final validation for email, URL, and website
    final_entities = []
    for ent in combined_entities:
        label = ent.get(LABEL)
        value = ent.get(TEXT)

        if label == "email" and not is_valid_email(value):
            logger.info(f"Skipping invalid email: {value}")
            continue

        if label == "website" and not re.match(r'^(www\.)[^\s]+\.[a-zA-Z]{2,}$', value):
            logger.info(f"Skipping invalid website: {value}")
            continue

        if label == "URL" and not re.match(r'^https?://[^\s]+$', value):
            logger.info(f"Skipping invalid URL: {value}")
            continue

        final_entities.append(ent)

    return final_entities
