import os
import spacy
from spacy.tokens import Doc
from multiprocessing import Pool, set_start_method

from pre_post_processing import add_dynamic_patterns  # Customize if needed
from constants import *  # You can define labels, patterns, configs here

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ─────────────────────────────────────────────────────────────
# 1. CHUNKING FUNCTION
# ─────────────────────────────────────────────────────────────
def extract_chunks(text, chunk_size=10000, overlap_size=1000):
    """
    Splits the input text into overlapping chunks.
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap_size):
        start = i
        end = min(i + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
    return chunks

# ─────────────────────────────────────────────────────────────
# 2. PARALLEL-SAFE PREPROCESSING FUNCTION
# ─────────────────────────────────────────────────────────────
def preprocess_chunk(chunk):
    """
    Performs lightweight preprocessing. Add more if needed.
    """
    return chunk.strip().replace("\n", " ")

# ─────────────────────────────────────────────────────────────
# 3. MAIN PIPELINE FUNCTION
# ─────────────────────────────────────────────────────────────
def process_in_chunks_fast(text, spacy_model_path, config, chunk_size=10000, overlap_size=1000):
    """
    Parallel preprocessing + fast NLP processing using a single shared SpaCy model.
    """
    # Step 1: Chunk the text
    chunks = extract_chunks(text, chunk_size, overlap_size)
    print(f"[INFO] Total chunks: {len(chunks)}")

    # Step 2: Preprocess chunks in parallel
    set_start_method("spawn", force=True)
    with Pool() as pool:
        preprocessed_chunks = pool.map(preprocess_chunk, chunks)

    # Step 3: Combine all preprocessed text
    final_text = "\n".join(preprocessed_chunks)

    # Step 4: Load SpaCy and add dynamic patterns (if any)
    nlp = spacy.load(spacy_model_path, disable=["parser", "lemmatizer", "tagger"])  # Optional: speed-up
    add_dynamic_patterns(nlp, config)  # Your custom function (optional)

    # Step 5: Run NLP pipeline
    doc = nlp(final_text)
    print("[INFO] NLP processing complete.")
    return doc

# ─────────────────────────────────────────────────────────────
# 4. OPTIONAL: EXTRACT NER RESULTS FROM FINAL DOC
# ─────────────────────────────────────────────────────────────
def extract_entities(doc):
    """
    Converts extracted entities from SpaCy Doc into structured dictionary list.
    """
    return [
        {
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char
        }
        for ent in doc.ents
    ]

# ─────────────────────────────────────────────────────────────
# 5. USAGE EXAMPLE (Entry Point)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Load input text
    with open("input.txt", "r", encoding="utf-8") as f:
        full_text = f.read()

    # SpaCy model path (e.g., "en_core_web_sm" or custom path)
    spacy_model_path = "en_core_web_sm"  # or your custom model

    # Dummy config for dynamic patterns
    config = {}  # Define your rules here if needed

    # Process the text
    doc = process_in_chunks_fast(full_text, spacy_model_path, config)

    # Extract and print NER entities
    entities = extract_entities(doc)
    print("[INFO] Extracted Entities:")
    for ent in entities:
        print(ent)
