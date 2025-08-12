import re

def find_port_codes(text):
    """
    Finds port codes in the format:
    2 uppercase letters (country) + 3 uppercase letters/numbers (location).
    Example: INNSA, USNYC, JPTYO, INN01
    """
    pattern = r'\b[A-Z]{2}[A-Z0-9]{3}\b'
    return re.findall(pattern, text)

# Example usage
sample_text = """
Shipment from INNSA to USNYC via JPTYO.
Also check INN01 and FRPAR.
"""
print(find_port_codes(sample_text))

