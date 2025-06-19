import re
from constants import *

def add_dynamic_patterns(nlp, config, label=LABEL_ORG):
    """
    Adds dynamic patterns to spaCy's EntityRuler for a specific label.
    """
    pattern_list = config.get(ENTITY_PATTERNS, [])

    if ENTITY_RULER in nlp.pipe_names:
        ruler = nlp.get_pipe(ENTITY_RULER)
    else:
        ruler = nlp.add_pipe(ENTITY_RULER, before=NER_SUFFIX, config={OVERWRITE_ENTS: True})

    patterns = [{ER_LABEL: label, ER_PATTERN: pattern} for pattern in pattern_list]
    ruler.add_patterns(patterns)
    return nlp


def preprocess(text, config, logger):
    """
    Preprocess text using regex replacement patterns defined in the config.
    """
    patterns = config.get(PREPROCESSING_PATTERNS, [])
    for item in patterns:
        text = re.sub(item[ER_PATTERN], item[ER_REPLACE], text)
    return text.strip()


def filter_entities(text, entities, config, logger):
    """
    Filter out entities if they are preceded by certain context words within a range.
    """
    context_range = config.get(CONTEXT_RANGE, 30)
    patterns = config.get(POSTPROCESSING_PATTERNS, {})

    try:
        attendee_regex = re.compile(patterns.get(ATTENDEE_PATTERN, EMPTY_STRING))
        preparer_regex = re.compile(patterns.get(PREPARER_PATTERN, EMPTY_STRING))
        authorized_signatory_regex = re.compile(patterns.get(AUTHORIZED_SIGNATORY_PATTERN, EMPTY_STRING))
    except re.error as e:
        logger.error(LOGGER_ERROR.format(str(e)))
        return []

    filtered_entities = []

    for entity in entities:
        start_index = entity.get(START_INDEX, 0)
        preceding_start = max(start_index - context_range, 0)
        preceding_text = text[preceding_start:start_index].replace(NEWLINE, SPACE)

        if not (
            attendee_regex.search(preceding_text) or
            preparer_regex.search(preceding_text) or
            authorized_signatory_regex.search(preceding_text)
        ):
            filtered_entities.append(entity)

    return filtered_entities


def extract_emails(text):
    email_pattern = r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}"
    return re.findall(email_pattern, text)


def extract_name_email_pairs(text):
    pattern = r'([\w\s,\.\"\']+)<([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,})>'
    return re.findall(pattern, text)


def is_valid_email(text):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(email_regex, text)


def extract_urls(text):
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)


def extract_websites(text):
    website_pattern = r'\b(?:www\.)[^\s]+\.[a-zA-Z]{2,}\b'
    return re.findall(website_pattern, text)


def extract_regex_entities(text, ocr_results):
    """
    Extract valid emails, name-email pairs, URLs, and websites enriched with OCR metadata.
    """
    entities = []

    email_matches = extract_emails(text)
    name_email_pairs = extract_name_email_pairs(text)
    url_matches = extract_urls(text)
    website_matches = extract_websites(text)

    name_email_addresses = [email for _, email in name_email_pairs if is_valid_email(email)]
    remaining_emails = [e for e in email_matches if is_valid_email(e) and e not in name_email_addresses]

    def find_in_ocr(match_text):
        for block in ocr_results:
            if match_text in block.get("text", ""):
                return {
                    "x": block.get("x"),
                    "y": block.get("y"),
                    "width": block.get("width"),
                    "height": block.get("height"),
                    "ocr_text": block.get("text", ""),
                }
        return {}

    for name, email in name_email_pairs:
        if is_valid_email(email):
            coords = find_in_ocr(email)
            entities.append({
                TEXT: email,
                LABEL: "email",
                "name": name.strip(),
                START_INDEX: text.find(email),
                **coords
            })

    for email in remaining_emails:
        coords = find_in_ocr(email)
        entities.append({
            TEXT: email,
            LABEL: "email",
            START_INDEX: text.find(email),
            **coords
        })

    for url in url_matches:
        coords = find_in_ocr(url)
        entities.append({
            TEXT: url,
            LABEL: "URL",
            START_INDEX: text.find(url),
            **coords
        })

    for website in website_matches:
        coords = find_in_ocr(website)
        entities.append({
            TEXT: website,
            LABEL: "website",
            START_INDEX: text.find(website),
            **coords
        })

    return entities, email_matches


def Extract_website_and_email(text, config, ocr_results, logger):
    """
    Extract emails (including name-email pairs) and website URLs using regex from text and OCR.
    """
    try:
        if ocr_results:
            ocr_text = " ".join([block.get("text", "") for block in ocr_results])
            text += " " + ocr_text
        else:
            ocr_results = []

        entities, emails = extract_regex_entities(text, ocr_results)
        logger.info(f"Extracted {len(emails)} emails and {len(entities) - len(emails)} websites/URLs")
        return entities

    except Exception as e:
        logger.error(f"Error extracting email and website entities: {str(e)}")
        return []


def remove_duplicates(entities):
    """
    Remove duplicate entities based on their text and label.
    """
    unique_entities = []
    seen = set()
    for entity in entities:
        identifier = (entity.get(TEXT), entity.get(LABEL))
        if identifier not in seen:
            seen.add(identifier)
            unique_entities.append(entity)
    return unique_entities


def post_screening(entities, text, ocr_results, config, logger):
    """
    Final step to process entities: filter contextually, and extract email/website info.
    """
    filtered_entities = filter_entities(text, entities, config, logger)
    domain_entities = Extract_website_and_email(text, config, ocr_results, logger)
    combined_entities = filtered_entities + domain_entities

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

    final_entities = remove_duplicates(final_entities)
    return final_entities
