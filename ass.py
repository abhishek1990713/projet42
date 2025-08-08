
import re

def is_continuation(current_text):
    """
    Returns True if the current text starts a URL (i.e., starts with http or https).
    """
    current_text = current_text.strip().lower()
    return current_text.startswith("http://") or current_text.startswith("https://")

def merge_ocr_text(data, config, logger):
    """
    Merges OCR segments that appear to be parts of the same URL or logical string.
    """
    merged_results = []
    i = 0

    while i < len(data):
        current = data[i]
        current_text = preprocess(current[ENTITY_TEXT], config, logger)
        x = current.get("x", 0)
        y = current.get("y", 0)
        width = current.get("width", 0)
        height = current.get("height", 0)
        page = current.get("page", 1)
        merged_text = current_text

        # Check if current text indicates a URL or email continuation
        if (is_continuation(current_text) or re.search(r'\.(com|org|net|gov|edu|co|jp|in|us|de|uk)', current_text)) and i + 1 < len(data):
            next_entry = data[i + 1]
            next_text = preprocess(next_entry[ENTITY_TEXT], config, logger)

            print("\nnext_text:", next_text, "current_text:", current_text)

            # Merge text and update bounding box
            merged_text += next_text
            print("\nmerged_text:", merged_text)

            width = (next_entry["x"] + next_entry["width"]) - x
            height = max(height, next_entry["height"])
            i += 1  # Skip the next one since it was merged

        # Append merged or individual entry
        merged_results.append({
            ENTITY_TEXT: merged_text,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "page": page
        })

        i += 1

    return merged_results
