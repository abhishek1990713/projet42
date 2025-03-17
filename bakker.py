


import re
import pandas as pd

def sanitize_mrl2(mrl2):
    """Modify MRL_Second to replace everything after the first '<' with '<'."""
    first_lt_index = mrl2.find("<")  # Find the first occurrence of '<'
    if first_lt_index != -1:
        return mrl2[:first_lt_index] + "<" * (len(mrl2) - first_lt_index)
    return mrl2  # Return unchanged if no '<' found

def parse_mrz(mrl1, mrl2):
    """Extracts passport details from MRZ (Machine Readable Zone) lines and returns a DataFrame."""

    # Ensure MRZ lines are padded to at least 44 characters
    mrl1 = mrl1.ljust(44, "<")[:44]
    mrl2 = sanitize_mrl2(mrl2.ljust(44, "<")[:44])  # Apply sanitization

    # Extract document type (e.g., P, PD, PP)
    document_type = mrl1[:2].strip("<")

    # Extract issuing country code
    country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"

    # Extract surname and given names
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if names_part else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

    # Extract passport number
    passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) > 9 else "Unknown"

    # Extract nationality
    nationality = mrl2[10:13].strip("<") if len(mrl2) > 13 else "Unknown"

    # Date conversion function (YYMMDD → DD/MM/YYYY)
    def format_date(yyMMdd):
        if len(yyMMdd) != 6 or not yyMMdd.isdigit():
            return "Invalid Date"
        yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
        year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
        return f"{dd}/{mm}/{year}"

    # Extract date of birth and expiry date
    dob = format_date(mrl2[13:19]) if len(mrl2) > 19 else "Unknown"
    expiry_date = format_date(mrl2[21:27]) if len(mrl2) > 27 else "Unknown"

    # Extract gender
    gender_code = mrl2[20] if len(mrl2) > 20 else "X"
    gender_mapping = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}
    gender = gender_mapping.get(gender_code, "Unspecified")

    # Extract optional data
    optional_data = re.sub(r"<+$", "", mrl2[28:]).strip() if len(mrl2) > 28 else "N/A"

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
