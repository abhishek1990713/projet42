


import re
import pandas as pd

def parse_mrz(mrl1, mrl2):
    """Extracts passport details from MRZ (Machine Readable Zone) lines and returns a DataFrame."""

    # Ensure MRZ lines are at least 44 characters
    mrl1 = mrl1.ljust(44, "<")[:44]
    mrl2 = mrl2.ljust(44, "<")[:44]

    # Extract document type (e.g., P, PD, PP)
    document_type = mrl1[:2].strip("<")

    # Extract issuing country code
    country_code = mrl1[2:5].strip("<")

    # Extract surname and given names
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if len(names_part) > 0 else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

    # Extract passport number (first 9 characters from MRL_Second)
    passport_number = re.sub(r"<+$", "", mrl2[:9]) if len(mrl2) >= 9 else "Unknown"

    # Extract nationality (position 11-13)
    nationality = mrl2[10:13].strip("<") if len(mrl2) >= 13 else "Unknown"

    # Function to convert YYMMDD → DD/MM/YYYY format
    def format_date(yyMMdd):
        if len(yyMMdd) != 6 or not yyMMdd.isdigit():
            return "Invalid Date"
        yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
        year = f"19{yy}" if int(yy) > 30 else f"20{yy}"
        return f"{dd}/{mm}/{year}"

    # Extract date of birth (positions 14-19)
    dob = format_date(mrl2[13:19]) if len(mrl2) >= 19 else "Unknown"

    # Extract gender (position 20)
    gender_code = mrl2[20] if len(mrl2) >= 21 else "X"
    gender_mapping = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified"}
    gender = gender_mapping.get(gender_code, "Unspecified")

    # Extract expiry date (positions 21-27)
    expiry_date = format_date(mrl2[21:27]) if len(mrl2) >= 27 else "Unknown"

    # Extract optional data (remaining characters after position 28)
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
    df = pd.DataFrame(data, columns=["Label", "Extracted_text"])
    return df

