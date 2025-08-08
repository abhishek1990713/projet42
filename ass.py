import re

# Constants
ENTITY_TEXT = 'text'

# Dummy preprocess function (replace with your actual logic if needed)
def preprocess(text, config=None, logger=None):
    return text.strip()

# Helper to check if a text is a potential URL start or continuation
def is_continuation(text):
    """
    Returns True if the text likely starts or continues a URL.
    """
    text = text.strip().lower()
    return (
        text.startswith("http://") or
        text.startswith("https://") or
        bool(re.search(r'\.(com|org|net|gov|edu|co|jp|in|us|de|uk)', text))
    )

# Main function to merge segments
def merge_ocr_text(data, config=None, logger=None):
    """
    Merges OCR segments that form a URL or logical string split across multiple segments.
    """
    # Optional: sort for proper sequence
    data = sorted(data, key=lambda d: (int(d.get("page", 1)), d.get("y", 0), d.get("x", 0)))

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

        end_x = x + width
        end_y = y + height

        # If it looks like a start/continuation, try merging
        if is_continuation(current_text):
            j = i + 1
            while j < len(data):
                next_entry = data[j]
                next_text = preprocess(next_entry[ENTITY_TEXT], config, logger)

                # Merge unless it's a very short token (like isolated 'I' or 'X')
                if not re.match(r'^\w{1,2}$', next_text):
                    merged_text += next_text
                    end_x = max(end_x, next_entry.get("x", 0) + next_entry.get("width", 0))
                    end_y = max(end_y, next_entry.get("y", 0) + next_entry.get("height", 0))
                    j += 1
                else:
                    break

                # Stop if merged text looks like a full URL ending
                if re.search(r'\.(com|org|net|gov|edu|co|jp|in|us|de|uk)(\/|$)', merged_text):
                    break

            width = end_x - x
            height = end_y - y

            merged_results.append({
                ENTITY_TEXT: merged_text,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "page": page
            })

            i = j  # skip merged ones
        else:
            merged_results.append({
                ENTITY_TEXT: current_text,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "page": page
            })
            i += 1

    return merged_results

