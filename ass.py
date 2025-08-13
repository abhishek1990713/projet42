import re
import pandas as pd
import pycountry

# Load UN/LOCODE CSV
df = pd.read_csv(r"C:\Users\AS34751\Downloads\code-list.csv")  # columns: Country, Location, Name
df['LOCODE'] = df['Country'] + df['Location']
VALID_PORT_CODES = set(df['LOCODE'])

# Set of valid country codes
COUNTRY_CODES = {country.alpha_2 for country in pycountry.countries}

def find_port_codes_with_positions(text, ocr_data):
    """
    Finds valid UN/LOCODE port codes in text with start/end positions
    and corresponding OCR coordinates.

    Args:
        text (str): Full OCR merged text
        ocr_data (list): List of OCR dicts with keys ["text","x","y","width","height"]

    Returns:
        list: combined_entities with dicts containing
              {"entity": ..., "start": ..., "end": ..., "coords": [...]}
    """
    pattern = r'\b([A-Z]{2})([A-Z0-9]{3})\b'
    matches = list(re.finditer(pattern, text))

    combined_entities = []

    for match in matches:
        country, location = match.groups()
        code = country + location
        if country in COUNTRY_CODES and code in VALID_PORT_CODES:
            start_idx = match.start()
            end_idx = match.end()

            # Find OCR coords for this entity
            coords = []
            for item in ocr_data:
                if code in item["text"]:
                    coords.append({
                        "x": item["x"],
                        "y": item["y"],
                        "width": item["width"],
                        "height": item["height"]
                    })

            combined_entities.append({
                "entity": code,
                "start": start_idx,
                "end": end_idx,
                "coords": coords
            })

    return combined_entities

