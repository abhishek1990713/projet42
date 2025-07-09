def remove_overlapping_entities(ner_details):
    sorted_ner = sorted(ner_details, key=lambda x: x[OVERLAPPING_START_INDEX])
    non_overlapping_ner = []

    for entity in sorted_ner:
        overlapping = False

        for prev_entity in non_overlapping_ner:
            # Check for full containment
            if (
                entity[OVERLAPPING_START_INDEX



import os
import time
import json
import re
import xml.etree.ElementTree as ET
from gliner import GLINER
from configobj import ConfigObj
from pre_post_processing import *
from constants import *

# Function to clean OCR text using preprocessing patterns
def ocr_text(data, config, current_directory, logger):
    ocr_results = []
    for ner in data:
        ner[ENTITY_TEXT] = preprocess(ner[ENTITY_TEXT], config, logger)
        ocr_results.append(ner)

    text = SPACE.join(result[ENTITY_TEXT] for result in ocr_results)
    output_path = os.path.join(current_directory, OUTPUT_TEXT_FILE)

    with open(output_path, WRITE_MODE, encoding=ENCODING_TYPE) as file:
        file.write(text)

    logger.info(f"Cleaned OCR text saved to {output_path}")
    return text, ocr_results


def remove_punctuation(text):
    return re.sub(PUNCTUATION, EMPTY, text)


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


def extract_entities(text, entity_types, model, logger):
    chunk_size = 250
    overlap_size = 50
    all_entities = []
    words = text.split()
    try:
        chunks = chunk_text_with_overlap(text, chunk_size, overlap_size)
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
    except Exception as e:
        logger.error(f"Error in extracting entities: {e}")
    return all_entities


def detect_conflicting_spans(entities):
    seen_spans = {}
    conflicts = []
    for ent in entities:
        key = (ent['start'], ent['end'])
        if key in seen_spans:
            if ent['text'].strip() != seen_spans[key]['text'].strip():
                conflicts.append((seen_spans[key], ent))
        else:
            seen_spans[key] = ent
    return conflicts


def resolve_conflicts_by_longest_text(entities):
    span_map = {}
    for ent in entities:
        key = (ent['start'], ent['end'])
        if key not in span_map:
            span_map[key] = ent
        else:
            if len(ent['text']) > len(span_map[key]['text']):
                span_map[key] = ent
    return list(span_map.values())


def remove_all_overlapping_entities(entities):
    sorted_entities = sorted(entities, key=lambda x: (-(x['end'] - x['start']), x['start']))
    selected_entities = []
    for current in sorted_entities:
        overlap_found = False
        for accepted in selected_entities:
            if not (current['end'] <= accepted['start'] or current['start'] >= accepted['end']):
                overlap_found = True
                break
        if not overlap_found:
            selected_entities.append(current)
    return sorted(selected_entities, key=lambda x: x['start'])


def generate_ner_details(matched_text, ocr_match, start_index, end_index, label):
    matched_text = matched_text.strip()
    matched_list = matched_text.split()
    text_detail = {
        PAGE: ocr_match[0][PAGE],
        TEXT: matched_text,
        LABEL: label,
        X: int(ocr_match[0][X]),
        Y: int(ocr_match[0][Y]),
        WIDTH: int(ocr_match[0][WIDTH]),
        HEIGHT: int(ocr_match[0][HEIGHT]),
        START_INDEX: start_index,
        END_INDEX: end_index
    }
    return text_detail


def get_gliner_ner(doc_id, page_count, ref_no, ocr_results, config, current_directory, model_dir, logger):
    logger.info("Loading GLINER model...")
    try:
        config_ini = ConfigObj(CONFIG_FILE)
        model_path = config_ini[PARAMETER][MODEL_PATH]
        model = GLINER.from_pretrained(model_path, repo_type="local", local_files_only=True)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading GLiNER model: {e}")
        exit(1)

    entity_types = [
        "Person name", "Organization name", "Location", "GPE (Geo-political Entity)",
        "Company name", "Address", "Product name"
    ]

    text, ocr_results = ocr_text(ocr_results, config, current_directory, logger)
    print("\ntext:", text)

    entities = extract_entities(text, entity_types, model, logger)
    print("\nentities:", entities)

    conflicts = detect_conflicting_spans(entities)
    if conflicts:
        logger.warning(f"Conflicts detected: {len(conflicts)}")

    entities = resolve_conflicts_by_longest_text(entities)
    entities = remove_all_overlapping_entities(entities)

    unique_ners = set()
    ner_details = []
    indices_to_remove = set()
    seen = set()

    unique_ents = [ent for ent in entities if not (ent['text'] in seen or seen.add(ent['text']))]
    sorted_ents = sorted(unique_ents, key=lambda ent: len(ent['text'].split()), reverse=True)

    for ent in sorted_ents:
        if ent['text'].strip('.') and ent['text'].upper() not in unique_ners:
            entity_text = ent['text']
            start_index = ent['start']
            end_index = ent['end']
            label = ent['label']
            matches = entity_text.split()
            unique_ners.add(ent['text'].upper())

            for i, ner in enumerate(ocr_results):
                if i in indices_to_remove:
                    continue
                if remove_punctuation(ner[ENTITY_TEXT]) == remove_punctuation(entity_text):
                    indices_to_remove.add(i)
                    text_details = generate_ner_details(entity_text, [ner], start_index, end_index, label)
                    ner_details.append(text_details)
                    break

    logger.info("Removing overlapping entities...")
    ner_details = remove_overlapping_entities(ner_details)
    logger.info("Post-screening entities...")

    screened_entities = post_screening(ner_details, text, ocr_results, config, logger)
    xml_output = generate_xml(doc_id, page_count, screened_entities)
    logger.info("Generated XML output")

    output_path = os.path.join(current_directory, XML_OUTPUT_FILE)
    with open(output_path, WRITE_MODE, encoding=ENCODING_TYPE) as xml_file:
        xml_file.write(xml_output)

    return xml_output
