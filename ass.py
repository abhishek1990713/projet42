# GLiNER Enhanced Entity Pipeline with Smart Overlap Handling

import re
import os
from configobj import ConfigObj
import json
from gliner import GLINER
from constants import *
from pre_post_processing import *

# Chunking Function

def chunk_text_with_overlap(text, max_words, overlap):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append({
            "chunk_text": chunk,
            "start_word_index": start
        })
        if end >= len(words):
            break
        start = end - overlap
    return chunks

# Extract Entities from Chunks

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
                ent["start"] += offset
                ent["end"] += offset

                reconstructed = ' '.join(words[ent['start']:ent['end']])
                if ent["text"] != reconstructed:
                    logger.warning(f"Text mismatch: '{ent['text']}' != '{reconstructed}'")

            all_entities.extend(entities)
            logger.info(f"Chunk processed, entities found: {len(entities)}")

        return all_entities

    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return []

# Deduplicate Entities by Text (Optional)

def deduplicate_entities(entities):
    seen = set()
    unique_entities = []

    for ent in entities:
        key = ent['text'].strip().lower()
        if key not in seen:
            seen.add(key)
            unique_entities.append(ent)

    return unique_entities

# Smart Overlap Removal

def remove_overlapping_entities(ner_details):
    sorted_ner = sorted(
        ner_details,
        key=lambda x: (x[START_INDEX], -(x[END_INDEX] - x[START_INDEX]))
    )

    non_overlapping = []

    for current in sorted_ner:
        is_nested_duplicate = False

        for existing in non_overlapping:
            if (
                current[START_INDEX] >= existing[START_INDEX] and
                current[END_INDEX] <= existing[END_INDEX]
            ):
                if (
                    current[LABEL].lower() == existing[LABEL].lower() and
                    current[ENTITY_TEXT].strip().lower() == existing[ENTITY_TEXT].strip().lower()
                ):
                    is_nested_duplicate = True
                    break

        if not is_nested_duplicate:
            non_overlapping.append(current)

    return non_overlapping
