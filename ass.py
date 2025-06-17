
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
    Preprocess the input text using regex replacement patterns defined in the config.
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


# -------------------
# Enhanced Email & Website Extraction
# -------------------

def extract_emails(text):
    return re.findall(r'[\w\.-]+@[\w\-]+\.[a-zA-Z]{2,}', text)

def extract_name_email_pairs(text):
    return re.findall(r'([\w\s,\.\"\']+)<([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,})>', text)

def extract_websites(text):
    return re.findall(r'\b(?:www\.)[^\s]+\.[a-zA-Z]{2,}\b', text)

def extract_regex_entities(text):
    entities = []

    email_matches = extract_emails(text)
    name_email_pairs = extract_name_email_pairs(text)

    name_email_addresses = [email for _, email in name_email_pairs]
    remaining_emails = [e for e in email_matches if e not in name_email_addresses]

    for name, email in name_email_pairs:
        entities.append({TEXT: email, LABEL: "email", "name": name.strip(), "score": 1.0})

    for email in remaining_emails:
        entities.append({TEXT: email, LABEL: "email", "score": 1.0})

    for website in extract_websites(text):
        entities.append({TEXT: website, LABEL: "website", "score": 1.0})

    return entities, email_matches


def Extract_website_and_email(text, config, ocr_results, logger):
    """
    Extract emails (including name-email pairs) and website URLs using regex from text and OCR.
    """
    try:
        if ocr_results:
            ocr_text = " ".join([block.get("text", "") for block in ocr_results])
            text += " " + ocr_text

        entities, emails = extract_regex_entities(text)
        logger.info(f"Extracted {len(emails)} emails and {len(entities) - len(emails)} websites from text.")
        return entities

    except Exception as e:
        logger.error(f"Error extracting email and website entities: {str(e)}")
        return []


# -------------------
# Final Screening Step
# -------------------

def post_Screening(entities, text, ancillary_entities, ocr_results, config, logger):
    """
    Final step to process entities: filter contextually, and extract email/website info.
    """
    filtered_entities = filter_entities(text, entities, config, logger)
    domain_entities = Extract_website_and_email(text, config, ocr_results, logger)
    final_entities = filtered_entities + domain_entities
    return final_entities



# Mock logger
class MockLogger:
    def info(self, msg): print("[INFO]", msg)
    def error(self, msg): print("[ERROR]", msg)

# Mock constants if needed (comment out if imported from constants.py)
LABEL = "label"
TEXT = "text"
START_INDEX = "start_index"
NEWLINE = "\n"
SPACE = " "
LABEL_ORG = "ORG"
ENTITY_PATTERNS = "entity_patterns"
ENTITY_RULER = "entity_ruler"
NER_SUFFIX = "ner"
OVERWRITE_ENTS = "overwrite_ents"
ER_LABEL = "label"
ER_PATTERN = "pattern"
ER_REPLACE = "replace"
PREPROCESSING_PATTERNS = "preprocessing_patterns"
POSTPROCESSING_PATTERNS = "postprocessing_patterns"
CONTEXT_RANGE = "context_range"
ATTENDEE_PATTERN = "attendee_pattern"
PREPARER_PATTERN = "preparer_pattern"
AUTHORIZED_SIGNATORY_PATTERN = "authorized_signatory_pattern"
EMPTY_STRING = ""
LOGGERB = "Regex error: {error_msg}"

# Sample input text
sample_text = """
John Doe <john.doe@example.com> and Jane <jane@work.org> were the contacts.
Visit www.hcltech.com or http://openai.com for more info.
"""

# Sample entities (pretend extracted entities from some NER tool)
sample_entities = [
    {TEXT: "John Doe", START_INDEX: 0, LABEL: "person"},
    {TEXT: "Jane", START_INDEX: 40, LABEL: "person"}
]

# Sample ancillary entities and OCR results
ancillary_entities = []
ocr_results = [{"text": "For support contact support@hcltech.com"}]

# Mock config
mock_config = {
    CONTEXT_RANGE: 30,
    POSTPROCESSING_PATTERNS: {
        ATTENDEE_PATTERN: r"\battendee\b",
        PREPARER_PATTERN: r"\bprepared by\b",
        AUTHORIZED_SIGNATORY_PATTERN: r"\bauthorized signatory\b"
    }
}

# Run the function
logger = MockLogger()
results = post_Screening(sample_entities, sample_text, ancillary_entities, ocr_results, mock_config, logger)

# Print results
print("\n[Final Entities]")
for r in results:
    print(r)

