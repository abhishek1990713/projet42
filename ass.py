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

