import re

# Step 1: Clean the extracted text (e.g., fix "www. something" → "www.something")
text = re.sub(r'www\.\s+', 'www.', text)

# Step 2: Merge OCR result bounding boxes for full URL
def merge_url_parts(ocr_results):
    url_keywords = ['www.', 'http', '.com', '.org', '.net', '.co.', '.in']
    url_parts = []
    merged_results = []
    skip_indexes = set()

    for i, item in enumerate(ocr_results):
        txt = item['text']
        if any(k in txt for k in url_keywords):
            url_parts.append((i, item))

    if url_parts:
        combined_text = ''
        min_x = float('inf')
        min_y = float('inf')
        max_x = 0
        max_y = 0
        page = url_parts[0][1]['page']

        for idx, part in url_parts:
            combined_text += part['text']
            min_x = min(min_x, part['x'])
            min_y = min(min_y, part['y'])
            max_x = max(max_x, part['x'] + part['width'])
            max_y = max(max_y, part['y'] + part['height'])
            skip_indexes.add(idx)

        merged_results.append({
            'text': combined_text,
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y,
            'page': page
        })

    # Add back non-URL parts
    for i, item in enumerate(ocr_results):
        if i not in skip_indexes:
            merged_results.append(item)

    return merged_results

# Apply merging logic
ocr_results = merge_url_parts(ocr_results)

# Final print
print('text:', text)
print('ocr_results:', ocr_results)


