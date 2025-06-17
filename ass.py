

def post_Screening(entities, text, ancillary_entities, ocr_results, config, logger):
    """
    Final post-processing step: filters entities by context and validates extracted domain/email entities.
    Only valid emails are included in the final output.
    """
    # Step 1: Contextual filtering
    filtered_entities = filter_entities(text, entities, config, logger)

    # Step 2: Extract domain/email entities using regex
    domain_entities, _ = extract_regex_entities(text)

    # Step 3: Merge all entities
    combined_entities = filtered_entities + domain_entities

    # Step 4: Apply post-filtering (e.g., remove invalid emails)
    final_entities = []
    for ent in combined_entities:
        label = ent.get(LABEL)
        value = ent.get(TEXT)

        if label == "email" and not is_valid_email(value):
            logger.info(f"Skipping invalid email in final entities: {value}")
            continue

        final_entities.append(ent)

    return final_entities
