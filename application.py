
import os
import json
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

# Optional label alias mapping
label_alias = {
    "passport_number": "id_number",
    "gpe": "location",
    "currency": "money"
    # Add more aliases as needed
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

# Entity extraction with confidence filtering and alias mapping
def extract_entities(text, entity_types, confidence_threshold=0.7):
    chunks = chunk_text_with_overlap(text)
    all_entities = []
    for chunk in chunks:
        try:
            entities = model.predict_entities(chunk, entity_types)
            for entity in entities:
                if entity.get("score", 1.0) >= confidence_threshold:
                    label = label_alias.get(entity["label"], entity["label"])
                    all_entities.append({
                        "text": entity["text"].strip(),
                        "label": label,
                        "score": round(entity.get("score", 1.0), 4)
                    })
        except Exception as e:
            print(f"Error processing chunk: {e}")
    return all_entities

# Deduplicate entities
def deduplicate_entities(entities):
    seen = set()
    unique_entities = []
    for e in entities:
        key = (e["text"].strip().lower(), e["label"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)
    return unique_entities

# Process all text files in a folder
def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(input_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            entities = extract_entities(text, entity_types)
            deduped = deduplicate_entities(entities)
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
