import re

def parse_mrz(mrl1, mrl2):
    # Ensure the MRZ lines have at least some content
    mrl1 = mrl1.ljust(44, "<")[:44]  # Pad with "<" if OCR missed characters
    mrl2 = mrl2.ljust(44, "<")[:44]

    # Detect document type (`P`, `PD`, `PP`, etc.)
    document_type = mrl1[:2].strip("<")

    # Extract issuing country
    country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"

    # Extract and clean name fields
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if names_part else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

    # Extract passport number safely
    passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) > 9 else "Unknown"

    # Extract nationality
    nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else "Unknown"

    # Convert YYMMDD to DD/MM/YYYY, handling missing values
    def format_date(yyMMdd):
        if len(yyMMdd) != 6 or not yyMMdd.isdigit():
            return "Invalid Date"
        yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
        year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
        return f"{dd}/{mm}/{year}"

    # Extract dates safely
    dob = format_date(mrl2[13:19]) if len(mrl2) > 19 else "Unknown"
    expiry_date = format_date(mrl2[21:27]) if len(mrl2) > 27 else "Unknown"

    # Extract gender
    gender_code = mrl2[20] if len(mrl2) > 20 else "X"
    gender_mapping = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}
    gender = gender_mapping.get(gender_code, "Unspecified")

    # Extract optional data safely (ignore trailing `<` characters)
    optional_data = re.sub(r"<+$", "", mrl2[28:]).strip() if len(mrl2) > 28 else "N/A"

    extracted_info = {
        "Document Type": document_type,
        "Issuing Country": country_code,
        "Surname": surname,
        "Given Names": given_names,
        "Passport Number": passport_number,
        "Nationality": nationality,
        "Date of Birth": dob,
        "Gender": gender,
        "Expiry Date": expiry_date,
        "Optional Data": optional_data if optional_data else "N/A",
    }

    return extracted_info

# Example MRZ Inputs (covering all edge cases)
test_cases = [
    ("PDCHNYANG<<ZHAO<<<<<<<<<<<<<<<<<<<<<<<<<<<<<", "DE00000003CHN8509037F2611158NBOONFNB<<<<A912"),
    ("PPCANMARTIN<<SARAH<<<<<<<<<<<<<<<<<<<<<<<<<<", "P123456AA0CAN9008010F3301144<<<<<<<<<<<<<<06"),
    ("PDRUSSMIRNOVA<<VALENTINA<<<<<<<<<<<<<<<<<<<<", "1100000000RUS8008046F0902274<<<<<<<<<<<<<<08"),
    ("P<GBRSMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<", "1234567890GBR8505057M3001012<<<<<<<<<<<<<<00"),
    ("P<CANDOE<<JANE<ELIZABETH", "9876543210CAN9212237F26061"),  # Incomplete second line
]

# Run test cases
for i, (mrl1, mrl2) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    passport_info = parse_mrz(mrl1, mrl2)
    for key, value in passport_info.items():
        print(f"{key}: {value}")
