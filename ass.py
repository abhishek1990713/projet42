import os
import spacy
from spacy.tokens import Doc
import time
from multiprocessing import Pool, set_start_method

from pre_post_processing import *
from constants import *

os.environ["TOKENIZERS_PARALLELISM"] = "false"

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


def preprocess_chunk(chunk):
    """
    Dummy preprocessing in parallel. You can expand this if needed.
    """
    return chunk  # You could add cleanup, lowercasing, regex etc.


def process_in_chunks_fast(text, spacy_model_path, config, chunk_size=10000, overlap_size=1000):
    """
    Fast version that parallelizes preprocessing and processes all chunks with a single SpaCy call.
    """
    # Step 1: Chunk the text
    chunks = extract_chunks(text, chunk_size, overlap_size)
    print(f"Total chunks: {len(chunks)}")

    # Step 2: Preprocess in parallel
    set_start_method("spawn", force=True)
    with Pool() as pool:
        preprocessed_chunks = pool.map(preprocess_chunk, chunks)

    # Step 3: Concatenate all preprocessed chunks
    final_text = "\n".join(preprocessed_chunks)

    # Step 4: Run SpaCy NLP on combined text using single shared Vocab
    nlp = spacy.load(spacy_model_path)
    add_dynamic_patterns(nlp, config)

    doc = nlp(final_text)
    return doc
