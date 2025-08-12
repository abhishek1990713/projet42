import re

def find_port_code_and_name(text):
    """
    Finds port code (UN/LOCODE) and port name in the text.
    Handles formats like:
    INNSA - Nhava Sheva
    USNYC: New York
    JPTYO Tokyo
    """
    # \b([A-Z]{2}[A-Z0-9]{3})\b → Port code (2 letters + 3 letters/numbers)
    # [\s\-:]+ → Separator (space, dash, or colon)
    # ([A-Za-z][A-Za-z\s]+) → Port name (starts with a letter, can have spaces)
    pattern = r'\b([A-Z]{2}[A-Z0-9]{3})\b[\s\-:]+([A-Za-z][A-Za-z\s]+)'
    
    matches = re.findall(pattern, text)
    return matches

# Example usage
sample_text = """
Shipment leaves from INNSA - Nhava Sheva and goes to USNYC: New York.
Final stop JPTYO Tokyo.
"""

results = find_port_code_and_name(sample_text)
for code, name in results:
    print(f"Port Code: {code}, Port Name: {name.strip()}")


