def extract_entities(text, entity_types, model, logger):
    chunk_size = 250
    overlap_size = 50

    try:
        chunks = chunk_text_with_overlap(text, chunk_size, overlap_size)
        all_entities = []

        words = text.split()

        for chunk in chunks:
            chunk_text = chunk["chunk_text"]
            offset = chunk["start_word_index"]

            entities = model.predict_entities(chunk_text, entity_types)

            for ent in entities:
                # Adjust the entity's start/end indices relative to full text
                ent["start"] += offset
                ent["end"] += offset

                # Optional: validate extracted text matches original
                reconstructed_text = ' '.join(words[ent["start"]:ent["end"]])
                if ent["text"] != reconstructed_text:
                    logger.warning(f"Text mismatch: Entity='{ent['text']}' vs Reconstructed='{reconstructed_text}'")

            all_entities.extend(entities)
            print("\nChunk processed, entities found:", len(entities))

        return all_entities

    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return []
