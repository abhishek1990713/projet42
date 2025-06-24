
import os
import spacy
from spacy.tokens import Doc
import time
from constants import *  # your constant strings/config
from pre_post_processing import add_dynamic_patterns  # assumed available

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def create_chunks(text, chunk_size=10000, overlap_size=1000):
    """
    Splits the input text into overlapping chunks.
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap_size):
        start = i
        end = min(i + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        if end == len(text):
            break
    return chunks


def process_in_chunks(text, spacy_model_path, config, chunk_size=10000, overlap_size=1000):
    """
    Safely processes text in chunks using a shared SpaCy NLP model.
    Avoids multiprocessing to ensure Vocab consistency.
    """
    start_time = time.time()
    print("[INFO] Loading SpaCy model...")
    nlp = spacy.load(spacy_model_path)
    add_dynamic_patterns(nlp, config)

    print("[INFO] Creating chunks...")
    chunks = create_chunks(text, chunk_size, overlap_size)
    print(f"[INFO] Total chunks created: {len(chunks)}")

    docs = []
    for idx, chunk in enumerate(chunks):
        print(f"[INFO] Processing chunk {idx + 1}/{len(chunks)}")
        doc = nlp(chunk)
        docs.append(doc)

    merged_doc = Doc.from_docs(docs)
    print(f"[INFO] Sequential processing complete in {time.time() - start_time:.2f} seconds.")
    return merged_doc


def fast_parallel_processing(text, spacy_model_path, config, chunk_size=10000, overlap_size=1000):
    """
    Fast version using SpaCy's built-in `nlp.pipe` with multiprocessing.
    Suitable for large texts; still safe since SpaCy manages Vocab internally.
    """
    start_time = time.time()
    print("[INFO] Loading SpaCy model with multiprocessing...")
    nlp = spacy.load(spacy_model_path)
    add_dynamic_patterns(nlp, config)

    chunks = create_chunks(text, chunk_size, overlap_size)
    print(f"[INFO] Total chunks: {len(chunks)}")

    print("[INFO] Processing in parallel using nlp.pipe() ...")
    docs = list(nlp.pipe(chunks, batch_size=4, n_process=2))  # Adjust based on your CPU

    merged_doc = Doc.from_docs(docs)
    print(f"[INFO] Parallel processing complete in {time.time() - start_time:.2f} seconds.")
    return merged_doc


# Example usage
if __name__ == "__main__":
    # Dummy setup – replace with real input
    test_text = "This is a long text. " * 10000  # Simulated large text
    model_path = "en_core_web_sm"  # Replace with your SpaCy model path
    config = {}  # Add your dynamic pattern config

    # Choose mode:
    # merged_doc = process_in_chunks(test_text, model_path, config)  # Safe mode
    merged_doc = fast_parallel_processing(test_text, model_path, config)  # Fast mode

    # Example output
    for ent in merged_doc.ents:
        print(f"{ent.text} ({ent.label_})")
