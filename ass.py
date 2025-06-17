

import re
from constants import *

def add_dynamic_patterns(nlp, config, label=LABEL_ORG):
    pattern_list = config.get(ENTITY_PATTERNS, [])
    if ENTITY_RULER in nlp.pipe_names:
        ruler = nlp.get_pipe(ENTITY_RULER)
    else:
        ruler = nlp.add_pipe(ENTITY_RULER, before=NER_SUFFIX, config={OVERWRITE_ENTS: True})
    patterns = [{ER_LABEL: label, ER_PATTERN: pattern} for pattern in pattern_list]
    ruler.add_patterns(patterns)
    return nlp

def preprocess(text, config, logger):
    patterns = config.get(PREPROCESSING_PATTERNS, [])
    for item in patterns:
        text = re.sub(item[ER_PATTERN], item[ER_REPLACE], text)
    return text.strip()

def filter_entities(text, entities, config, logger):
    context_range = config.get(CONTEXT_RANGE, 30)
    patterns = config.get(POSTPROCESSING_PATTERNS, {})

    try:
        attendee_regex = re.compile(patterns.get(ATTENDEE_PATTERN, EMPTY_STRING))
        preparer_regex = re.compile(patterns.get(PREPARER_PATTERN, EMPTY_STRING))
        authorized_signatory_regex = re.compile(patterns.get(AUTHORIZED_SIGNATORY_PATTERN, EMPTY_STRING))
    except re.error as e:
        logger.error(LOGGERB.format(error_msg=str(e)))
        attendee_regex = preparer_regex = authorized_signatory_regex = None

    filtered_entities = []
    for entity in entities:
        preceding_start = max(entity[START_INDEX] - context_range, 0)
        preceding_text = text[preceding_start:entity[START_INDEX]].replace(NEWLINE, SPACE)
        if not (
            (attendee_regex and attendee_regex.search(preceding_text)) or
            (preparer_regex and preparer_regex.search(preceding_text)) or
            (authorized_signatory_regex and authorized_signatory_regex.search(preceding_text))
        ):
            filtered_entities.append(entity)
    return filtered_entities

# -----------------------------
# Regex Utility Functions
# -----------------------------

def is_valid_email(text):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(email_regex, text)

def extract_emails(text):
    return re.findall(r'[\w\.-]+@[\w\-]+\.[a-zA-Z]{2,}', text)

def extract_name_email_pairs(text):
    return re.findall(r'([\w\s,\.\"\']+)<([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,})>', text)

def extract_websites(text):
    return re.findall(r'\b(?:www\.)[^\s]+\.[a-zA-Z]{2,}\b', text)

def extract_urls(text):
    return re.findall(r'https?://[^\s]+', text)

def extract_regex_entities(text):
    entities = []

    email_matches = extract_emails(text)
    name_email_pairs = extract_name_email_pairs(text)
    name_email_addresses = [email for _, email in name_email_pairs]
    remaining_emails = [e for e in email_matches if e not in name_email_addresses]

    for name, email in name_email_pairs:
        if is_valid_email(email):
            entities.append({TEXT: email, LABEL: "email", "name": name.strip()})

    for email in remaining_emails:
        if is_valid_email(email):
            entities.append({TEXT: email, LABEL: "email"})

    for website in extract_websites(text):
        entities.append({TEXT: website, LABEL: "website"})

    for url in extract_urls(text):
        entities.append({TEXT: url, LABEL: "url"})

    return entities, email_matches

# -----------------------------
# Email/Website/URL Extraction
# -----------------------------

def Extract_website_and_email(text, config, ocr_results, logger):
    try:
        if ocr_results:
            ocr_text = " ".join([block.get("text", "") for block in ocr_results])
            text += " " + ocr_text

        entities, emails = extract_regex_entities(text)
        logger.info(f"Extracted {len(emails)} emails and {len(entities) - len(emails)} other URLs/websites.")
        return entities

    except Exception as e:
        logger.error(f"Error extracting email/website/URL entities: {str(e)}")
        return []

# -----------------------------
# Final Screening
# -----------------------------

def post_Screening(entities, text, ancillary_entities, ocr_results, config, logger):
    filtered_entities = filter_entities(text, entities, config, logger)
    domain_entities = Extract_website_and_email(text, config, ocr_results, logger)
    final_entities = filtered_entities + domain_entities
    return final_entities
