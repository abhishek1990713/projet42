import re

def parse_mrl1(mrl1):
    match = re.match(r'P<([A-Z]{3})([A-Z]+)<<([A-Z]+)', mrl1)
    import re

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
    # Debug: Print extracted text before processing
    print("Raw MRL2:", mrl2)
    
    pattern = r'([A-Z0-9<]+)<([A-Z]{3})(\d{6})([MFX])(\d{6})([A-Z]{3})'
    match = re.match(pattern, mrl2)

    if match:
        return {
            "passport_number": match.group(1).replace('<', ''),
            "country_code": match.group(2),
            "birth_date": match.group(3),
            "sex": match.group(4),
            "expiry_date": match.group(5),
            "nationality": match.group(6)
        }

    print("MRL2 Parsing Failed:", mrl2)
    return None

# Example Inputs (Ensure they match your actual OCR output)
mrl1 = "P<JPNYAMADA<<TARO<<<<<<<<<<<<<<"
mrl2 = "AB1234567<JPN8201017M2901018JPN<<<<<<<<<"

print(parse_mrl1(mrl1))
print(parse_mrl2(mrl2))


