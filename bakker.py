


import re
import pandas as pd

def sanitize_mrl2(mrl2):
    """Modify MRL_Second to replace everything after the first '<' with '<'."""
    first_lt_index = mrl2.find("<")  # Find the first occurrence of '<'
    if first_lt_index != -1:
        return mrl2[:first_lt_index] + "<" * (len(mrl2) - first_lt_index)
    return mrl2  # Return unchanged if no '<' found

def find_nationality_index(mrl2):
    """Find the index where nationality (A-Z) starts in MRL_Second."""
    match = re.search(r"[A-Z]{3}", mrl2)  # Look for three consecutive uppercase letters
    return match.start() if match else None

def format_date(yyMMdd):
    """Convert YYMMDD to DD/MM/YYYY format."""
    if len(yyMMdd) != 6 or not yyMMdd.isdigit():
        return "Invalid Date"
    yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
    year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
    return f"{dd}/{mm}/{year}"

def parse_mrz(mrl1, mrl2):
    """Extracts passport details from MRZ lines and returns a DataFrame."""

    # Ensure MRZ lines are padded correctly
    mrl1 = mrl1.ljust(44, "<")[:44]
    mrl2 = sanitize_mrl2(mrl2.ljust(44, "<")[:44])

    # Extract document type
    document_type = mrl1[:2].strip("<")

    # Extract issuing country
    country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"

    # Extract surname and given names
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if names_part else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

    # Find nationality index dynamically
    nationality_idx = find_nationality_index(mrl2)
    
    if nationality_idx:
        passport_number = mrl2[:nationality_idx].strip("<")
        nationality = mrl2[nationality_idx:nationality_idx + 3]
        dob = format_date(mrl2[nationality_idx + 3:nationality_idx + 9])
        gender_code = mrl2[nationality_idx + 9] if len(mrl2) > nationality_idx + 9 else "X"
        expiry_date = format_date(mrl2[nationality_idx + 10:nationality_idx + 16])
        optional_data = mrl2[nationality_idx + 17:].strip("<")
    else:
        passport_number, nationality, dob, gender_code, expiry_date, optional_data = "Unknown", "Unknown", "Invalid Date", "X", "Invalid Date", "N/A"

    # Map gender code
    gender_mapping = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}
    gender = gender_mapping.get(gender_code, "Unspecified")

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
    df = pd.DataFrame(data, columns=["Label", "Extracted_Text"])
    return df
