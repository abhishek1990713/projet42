

def safe_find_text(elem, tag):
    found = elem.find(f'ns:{tag}', namespace)
    return found.text if found is not None else None

for field in fields.findall('ns:Field', namespace):
    label = safe_find_text(field, 'LabelName')
    value = safe_find_text(field, 'Value')
    x = safe_find_text(field, 'RectangleX')
    y = safe_find_text(field, 'RectangleY')
    w = safe_find_text(field, 'RectangleWidth')
    h = safe_find_text(field, 'RectangleHeight')

    if None in [x, y, w, h]:
        print(f"Skipping a field due to missing coordinates: {label}")
        continue

    x, y, w, h = map(int, [x, y, w, h])

    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(image, f"{label}: {value}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 1)
