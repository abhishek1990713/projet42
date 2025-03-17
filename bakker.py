

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

df = parse_mrz(mrl1, mrl2)
print(df)
import re
import pandas as pd

def sanitize_mrl2(mrl2):
    """Modify MRL_Second to replace everything after the first '<' with '<'."""
    first_lt_index = mrl2.find("<")
    if first_lt_index != -1:
        return mrl2[:first_lt_index] + "<" * (len(mrl2) - first_lt_index)
    return mrl2  

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

    # Extract passport number (always first 9 characters)
    passport_number = mrl2[:9]

    # Find nationality (first occurrence of three consecutive uppercase letters)
    nationality_match = re.search(r"[A-Z]{3}", mrl2)
    nationality_idx = nationality_match.start() if nationality_match else None

    if nationality_idx is not None:
        nationality = mrl2[nationality_idx:nationality_idx + 3]

        # Detect gender (first 'M' or 'F' after nationality)
        gender_match = re.search(r"[MF]", mrl2[nationality_idx + 3:])
        gender_idx = gender_match.start() + nationality_idx + 3 if gender_match else None

        if gender_idx is not None:
            gender_code = mrl2[gender_idx]
            dob = format_date(mrl2[nationality_idx + 3:gender_idx])  # DOB is between nationality and gender
            expiry_date = format_date(mrl2[gender_idx + 1:gender_idx + 7])  # Expiry date comes after gender
        else:
            gender_code, dob, expiry_date = "X", "Invalid Date", "Invalid Date"
    else:
        nationality, gender_code, dob, expiry_date = "Unknown", "X", "Invalid Date", "Invalid Date"

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
    ]

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=["Label", "Extracted_Text"])
    return df
