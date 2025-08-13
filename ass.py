import re
import pandas as pd
import pycountry

# Load UN/LOCODE CSV (download from UNECE site)
# File should have columns: Country, Location, Name
df = pd.read_csv(r"C:\Users\AS34751\Downloads\code-list.csv")

# Create LOCODE column and sets for validation
df['LOCODE'] = df['Country'] + df['Location']
VALID_PORT_CODES = set(df['LOCODE'])
COUNTRY_CODES = {country.alpha_2 for country in pycountry.countries}

def find_real_port_codes(ocr_data):
    """
    Finds valid port codes from OCR JSON data.
    ocr_data: list of dicts with keys: text, x, y, width, height
    Returns a list of entities with text, start, end, x, y, width, height
    """
    combined_entities = []
    pattern = r'\b([A-Z]{2})([A-Z0-9]{3})\b'

    for item in ocr_data:
        text = item.get('text', '').strip()
        for match in re.finditer(pattern, text):
            country, location = match.groups()
            code = country + location

            if country in COUNTRY_CODES and code in VALID_PORT_CODES:
                entity = {
                    "text": code,
                    "start": match.start(),
                    "end": match.end(),
                    "x": item.get('x'),
                    "y": item.get('y'),
                    "width": item.get('width'),
                    "height": item.get('height')
                }
                combined_entities.append(entity)

    return combined_entities


# ===== Example Usage =====
if __name__ == "__main__":
    # Example OCR JSON data
    ocr_results = [
        {"text": "The shipment departed from INMUM", "x": 100, "y": 200, "width": 50, "height": 10},
        {"text": "Next port is USSFO", "x": 150, "y": 250, "width": 60, "height": 12},
        {"text": "Random text", "x": 200, "y": 300, "width": 70, "height": 15}
    ]

    entities = find_real_port_codes(ocr_results)
    print(entities)
