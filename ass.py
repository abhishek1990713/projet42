import re
import pycountry  # pip install pycountry

# Create a set of all valid ISO country codes
COUNTRY_CODES = {country.alpha_2 for country in pycountry.countries}

def find_port_codes(text):
    """
    Finds port codes where:
    - First 2 characters are valid ISO country codes.
    - Next 3 characters are uppercase letters or numbers.
    """
    pattern = r'\b([A-Z]{2})([A-Z0-9]{3})\b'
    matches = re.findall(pattern, text)

    valid_codes = []
    for country, location in matches:
        if country in COUNTRY_CODES:
            valid_codes.append(country + location)
    return valid_codes

# Example usage
sample_text = """
Shipment from INNSA to USNYC via JPTYO.
Also check INN01 and FRPAR. Random ABCDE should be ignored.
"""
print(find_port_codes(sample_text))
