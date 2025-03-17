


import re
import pandas as pd

def parse_mrz(mrl1, mrl2):
    """Extracts passport details from MRZ (Machine Readable Zone) lines and returns a DataFrame."""

    # Ensure MRZ lines are properly padded to at least 44 characters
    mrl1 = mrl1.ljust(44, "<")[:44]
    mrl2 = mrl2.ljust(44, "<")[:44]

    print("DEBUG - MRZ Line 1:", mrl1)  # Debugging MRZ Line 1
    print("DEBUG - MRZ Line 2:", mrl2)  # Debugging MRZ Line 2

    # Extract document type (P)
    document_type = mrl1[:2].strip("<")

    # Extract issuing country (USA)
    country_code = mrl1[2:5].strip("<")

    # Extract surname and given names
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if len(names_part) > 0 else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

    print("DEBUG - Surname:", surname)  # Debugging Surname Extraction
    print("DEBUG - Given Names:", given_names)  # Debugging Given Names Extraction

    # Extract passport number (first 9 characters of second MRZ line)
    passport_number = mrl2[:9].strip("<")

    # Extract nationality (positions 10-12)
    nationality = mrl2[10:13].strip("<")

    # Function to convert YYMMDD → DD/MM/YYYY format
    def format_date(yyMMdd):
        if not re.match(r"^\d{6}$", yyMMdd):  # Ensure it's a 6-digit number
            return "Invalid Date"
        yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
        year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
        return f"{dd}/{mm}/{year}"

    # Extract date of birth (positions 13-18)
    dob = format_date(mrl2[13:19])
    print("DEBUG - Date of Birth:", dob)  # Debugging Date of Birth Extraction

    # Extract gender (position 20)
    gender_code = mrl2[20] if len(mrl2) >= 21 else "<"
    gender_mapping = {"M": "Male", "F": "Female"}
    gender = gender_mapping.get(gender_code, "Unspecified")

    print("DEBUG - Gender Code:", gender_code, "Parsed as:", gender)  # Debugging Gender Extraction

    # Extract expiry date (positions 21-26)
    expiry_date = format_date(mrl2[21:27])
    print("DEBUG - Expiry Date:", expiry_date)  # Debugging Expiry Date Extraction

    # Extract optional data (everything after position 28)
    optional_data = re.sub(r"<+$", "", mrl2[28:]).strip() if len(mrl2) > 28 else "N/A"

    print("DEBUG - Optional Data:", optional_data)  # Debugging Optional Data Extraction

    # Create structured data for DataFrame
    data = [
        ("Document Type", document_type),
        ("Issuing Country", country_code),
        ("Surname", surname),
        ("Given Names", given_names),
        ("Passport Number", passport_number),
        ("Nationality", nationality),
        ("Date of Birth", dob),
        ("Gender", gender),
        ("Expiry Date", expiry_date),
        ("Optional Data", optional_data if optional_data else "N/A"),
    ]

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=["Label", "Extracted_text"])
    return df
