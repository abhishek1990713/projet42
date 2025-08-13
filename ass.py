import re
import pandas as pd
import pycountry

# Load UN/LOCODE CSV (downloaded from UNECE site)
# CSV must have columns: Country, Location, Name
df = pd.read_csv(r"C:\Users\AS34751\Downloads\code-list.csv")
df['LOCODE'] = df['Country'] + df['Location']
VALID_PORT_CODES = set(df['LOCODE'])

# Set of valid ISO country codes
COUNTRY_CODES = {country.alpha_2 for country in pycountry.countries}


def find_port_codes_with_positions(text, ocr_data):
    """
    Finds valid UN/LOCODE port codes in the given text using OCR bounding box data.
    
    Args:
        text (str): Full OCR combined text.
        ocr_data (list[dict]): Each dict must have 'text', 'x', 'y', 'width', 'height', 'page'.
    
    Returns:
        list[dict]: Each dict contains page, text, label, x, y, width, height, start_index, end_index.
    """
    pattern = r'\b([A-Z]{2})([A-Z0-9]{3})\b'
    matches = re.finditer(pattern, text)
    
    results = []
    for match in matches:
        country, location = match.groups()
        code = country + location
        if country in COUNTRY_CODES and code in VALID_PORT_CODES:
            start_idx = match.start()
            end_idx = match.end()

            # Find the OCR segment that matches this text
            for seg in ocr_data:
                if code in seg['text']:
                    results.append({
                        "page": seg.get("page"),
                        "text": code,
                        "label": "PORT_CODE",
                        "x": seg.get("x"),
                        "y": seg.get("y"),
                        "width": seg.get("width"),
                        "height": seg.get("height"),
                        "start_index": start_idx,
                        "end_index": end_idx
                    })
                    break
    return results
