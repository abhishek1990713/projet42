import re

def clean_mrl2(mrl2):
    """ Fix OCR issues and missing separators in MRL2 """
    mrl2 = re.sub(r'[^A-Z0-9<]', '<', mrl2)  # Replace any non-alphanumeric/non-< characters with `<`
    mrl2 = re.sub(r'<+', '<', mrl2)  # Remove duplicate `<`
    
    # If the passport number and country code are joined, insert a `<`
    if re.match(r'^[A-Z0-9]{9,10}[A-Z]{3}', mrl2):
        mrl2 = mrl2[:10] + '<' + mrl2[10:]  # Insert `<` after passport number
    
    # Ensure the line has 44 characters
    mrl2 = mrl2.ljust(44, '<')
    
    return mrl2.strip()

def parse_mrl1(mrl1):
    match = re.match(r'P<([A-Z]{3})([A-Z]+)<<([A-Z<]+)', mrl1)
    if match:
        return {
            "document_type": "Passport",
            "country_code": match.group(1),
            "surname": match.group(2),
            "given_names": match.group(3).replace('<', ' ').strip()
        }
    print("MRL1 Parsing Failed:", mrl1)
    return None

def parse_mrl2(mrl2):
    print("Raw MRL2 before cleaning:", mrl2)
    
    mrl2 = clean_mrl2(mrl2)  # Fix OCR issues

    print("Cleaned MRL2:", mrl2)

    pattern = r'([A-Z0-9]+)<([A-Z]{3})(\d{6})([MFX])(\d{6})([A-Z]{3})'
    match = re.match(pattern, mrl2)

    if match:
        return {
            "passport_number": match.group(1),
            "country_code": match.group(2),
            "birth_date": match.group(3),
            "sex": match.group(4),
            "expiry_date": match.group(5),
            "nationality": match.group(6)
        }

    print("MRL2 Parsing Failed:", mrl2)
    return None

# Example Inputs
mrl1 = "P<GBRANGUILLA<SPECIMEN<<ANGELA<ZOE<<<<<<<<<<"
mrl2 = "9992026018GBD9501016F2911272<<<<<<<<<<<<<<00"  # Incorrect format

print(parse_mrl1(mrl1))
print(parse_mrl2(mrl2))

