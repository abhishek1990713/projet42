
import os
import json
import re
from rapidfuzz import fuzz  # You may need to install: pip install rapidfuzz
from gliner import GLiNER

# Load GLiNER model
model_path = "/home/ko19678/NER_gliner/model_gliner/glinerv2.5-pytorch-default-v1/gliner_model_v2.5"
model = GLiNER.from_pretrained(model_path)

# Expanded label list (GLiNER v2.5 + extended categories)
entity_types = [
    # Standard entity types
    "person", "organization", "location", "date", "time", "money", "percent", "event", "product", "work_of_art", "language",
    "law", "facility", "gpe", "ordinal", "cardinal", "quantity", "nationality", "religion", "ideology",
    "crime", "weapon", "vehicle", "disease", "medical_treatment", "medication", "anatomical_structure", "symptom",
    "email", "phone_number", "url", "username", "ip_address", "mac_address", "hashtag", "stock_ticker",

    # Technology
    "programming_language", "software", "hardware", "os", "protocol", "file_format", "api", "framework",

    # Science & Medicine
    "biological_process", "chemical_substance", "gene", "protein", "cell_type", "scientific_term", "academic_field",

    # Education
    "academic_degree", "university", "school_subject", "course_name", "teacher", "student",

    # Sports & Entertainment
    "sports_team", "sports_event", "sports_league", "tournament", "video_game", "movie", "tv_show",
    "book", "music_album", "song", "celebrity", "character",

    # Commerce
    "currency", "measurement_unit", "brand", "model", "material", "clothing", "food", "drink", "color",
    "price", "discount", "product_category", "review_score",

    # Natural & Geographic
    "animal", "plant", "weather", "terrain", "planet", "mountain", "river", "sea", "continent",

    # Government, Legal, and ID
    "government_agency", "document_type", "passport_number", "id_number", "case_number", "court", "judge",

    # Social Media and Communication
    "social_media_platform", "chat_app", "forum", "comment", "post", "reaction",

    # Miscellaneous
    "fictional_universe", "mythology", "ritual", "holiday", "festival", "artifact", "tool", "furniture"
]

# Label normalization map
label_aliases = {
    "org": "organization",
    "loc": "location",
    "place": "location",
    "name": "person",
    "e-mail": "email",
    "url_address": "url",
}

# Chunk text with overlap
def chunk_text_with_overlap(text, max_words=250, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + max_words]
        chunks.append(' '.join(chunk))
        i += max_words - overlap
    return chunks

# Entity extraction
def extract_entities(text, entity_types):
    chunks = chunk_text_with_overlap(text)
    all_entities = []
    for chunk in chunks:
        entities = model.predict_entities(chunk, entity_types)
        all_entities.extend(entities)
    return all_entities

# Advanced post-processing
def advanced_post_process(entities, label_aliases=None, confidence_threshold=0.6, fuzzy_threshold=90):
    """
    Advanced post-processing for entity extraction results.

    Args:
        entities (list): List of entity dicts with keys 'text', 'label', optionally 'score'.
        label_aliases (dict): Optional dict to normalize labels, e.g., {"org": "organization"}.
        confidence_threshold (float): Minimum score to keep an entity.
        fuzzy_threshold (int): Similarity ratio (0-100) to consider entities duplicates.

    Returns:
        List of cleaned and deduplicated entities.
    """

    if label_aliases is None:
        label_aliases = {}

    def is_valid(entity):
        text = entity["text"].strip()
        label = entity["label"].lower()
        score = entity.get("score", 1.0)

        # Filter by confidence
        if score < confidence_threshold or not text:
            return False

        # Basic regex validation for common types
        if label == "email":
            return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text))
        if label == "phone_number":
            return bool(re.match(r"\+?\d[\d\s\-]{7,}\d", text))
        if label == "url":
            return bool(re.match(r"https?://\S+", text))
        if label == "date":
            return bool(re.match(r"\d{4}-\d{2}-\d{2}", text))

        return True

    def is_duplicate(new_ent, existing_ents):
        # Check fuzzy text similarity and identical labels
        for ent in existing_ents:
            if ent["label"] == new_ent["label"]:
                similarity = fuzz.ratio(ent["text"].lower(), new_ent["text"].lower())
                if similarity >= fuzzy_threshold:
                    return True
        return False

    cleaned_entities = []
    for ent in entities:
        ent["label"] = label_aliases.get(ent["label"].lower(), ent["label"].lower())
        ent["text"] = ent["text"].strip()

        if not is_valid(ent):
            continue

        if not is_duplicate(ent, cleaned_entities):
            cleaned_entities.append(ent)

    # Remove entities fully contained inside longer entities of same label
    final_entities = []
    for ent in cleaned_entities:
        contained = False
        for other in cleaned_entities:
            if ent == other:
                continue
            if ent["label"] == other["label"] and ent["text"] in other["text"]:
                if len(ent["text"]) < len(other["text"]):
                    contained = True
                    break
        if not contained:
            final_entities.append(ent)

    return final_entities

# Process all text files in a folder
def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(input_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            entities = extract_entities(text, entity_types)
            deduped = advanced_post_process(entities, label_aliases=label_aliases, confidence_threshold=0.6)
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_folder, output_filename)
            with open(output_path, "w", encoding="utf-8") as out_file:
                json.dump(deduped, out_file, indent=2, ensure_ascii=False)
            print(f"Processed: {filename} -> {output_filename}")

# Example usage
if __name__ == "__main__":
    input_folder = "/home/ko19678/NER_gliner/New folder"
    output_folder = "/home/ko19678/NER_gliner/New folder"
    process_folder(input_folder, output_folder)
