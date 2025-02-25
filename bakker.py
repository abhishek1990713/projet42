
import re

def parse_mrz(mrl1, mrl2):
    # Ensure the MRZ lines have at least some content
    mrl1 = mrl1.ljust(44, "<")[:44]  # Fill missing characters with "<" up to 44 chars
    mrl2 = mrl2.ljust(44, "<")[:44]  

    # Extract issuing country (if available)
    country_code = mrl1[2:5] if len(mrl1) > 5 else "Unknown"

    # Extract and clean name fields
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip() if names_part else "Unknown"
    given_names = re.sub(r"<+", " ", names_part[1]).strip() if len(names_part) > 1 else "Unknown"

    # Extract passport number (handle missing parts)
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

    # Extract optional data safely
    optional_data = mrl2[28:].strip("<") if len(mrl2) > 28 else "N/A"

    extracted_info = {
        "Issuing Country": country_code,
        "Surname": surname,
        "Given Names": given_names,
        "Passport Number": passport_number,
        "Nationality": nationality,
        "Date of Birth": dob,
        "Gender": gender,
        "Expiry Date": expiry_date,
        "Optional Data": optional_data,
    }

    return extracted_info

# Example MRZ Inputs (including incomplete OCR outputs)
test_cases = [
    ("P<GBRSMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<", "1234567890GBR8505057M3001012<<<<<<<<<<<<<<00"),
    ("P<CANDOE<<JANE<ELIZABETH", "9876543210CAN9212237F26061"),  # Incomplete second line
    ("P<USAJOHNSON<<ALEXANDER", "ABC1234567USA89"),  # Very short second line
    ("P<FRA", "7654321098FRA7805059F"),  # Missing given names and expiry date
    ("", ""),  # Completely missing data
]

# Run test cases
for i, (mrl1, mrl2) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    passport_info = parse_mrz(mrl1, mrl2)
    for key, value in passport_info.items():
        print(f"{key}: {value}")
import re

def parse_mrz(mrl1, mrl2):
    # Validate MRZ length
    if len(mrl1) < 44 or len(mrl2) < 44:
        raise ValueError("Invalid MRZ format: Each line must be at least 44 characters long.")

    # Extract issuing country code
    country_code = mrl1[2:5]

    # Extract and clean name fields (handles <<, <, or missing separators)
    names_part = mrl1[5:].split("<<", 1)
    surname = re.sub(r"<+", " ", names_part[0]).strip()
    given_names = re.sub(r"<+", " ", names_part[1]) if len(names_part) > 1 else ""

    # Extract and clean passport number (strip trailing '<' characters)
    passport_number = re.sub(r"<+$", "", mrl2[:9])

    # Extract nationality code
    nationality = mrl2[10:13].strip("<")

    # Function to convert YYMMDD to DD/MM/YYYY with century handling
    def format_date(yyMMdd):
        if len(yyMMdd) != 6 or not yyMMdd.isdigit():
            return "Invalid Date"
        yy, mm, dd = yyMMdd[:2], yyMMdd[2:4], yyMMdd[4:6]
        year = f"19{yy}" if int(yy) > 30 else f"20{yy}"  # Assume 1930-2099 range
        return f"{dd}/{mm}/{year}"

    # Extract date of birth and expiry date
    dob = format_date(mrl2[13:19])
    expiry_date = format_date(mrl2[21:27])

    # Extract and normalize gender
    gender_code = mrl2[20]
    gender_mapping = {"M": "Male", "F": "Female", "X": "Unspecified", "<": "Unspecified", "": "Unspecified"}
    gender = gender_mapping.get(gender_code, "Unspecified")

    # Handle optional fields if present
    optional_data = mrl2[28:].strip("<")

    extracted_info = {
        "Issuing Country": country_code,
        "Surname": surname,
        "Given Names": given_names.strip(),
        "Passport Number": passport_number,
        "Nationality": nationality,
        "Date of Birth": dob,
        "Gender": gender,
        "Expiry Date": expiry_date,
        "Optional Data": optional_data if optional_data else "N/A",
    }

    return extracted_info

# Example MRZ Inputs (covering different edge cases)
test_cases = [
    ("P<GBRSMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<", "1234567890GBR8505057M3001012<<<<<<<<<<<<<<00"),
    ("P<CANDOE<<JANE<ELIZABETH<<<<<<<<<<<<<<", "9876543210CAN9212237F2606154<<<<<<<<<<<<<<00"),
    ("P<USAJOHNSON<<ALEXANDER<<<<<<<<<<<<<<", "ABC1234567USA8901018M3501015<<<<<<<<<<<<<<00"),
    ("P<FRA<<DUPONT<MARIE<<<<<<<<<<<<<<<<<<", "7654321098FRA7805059F2501011<<<<<<<<<<<<<<00"),
    ("P<DEUMÜLLER<<LUKAS<<<<<<<<<<<<<<<<<<<", "5432109876DEU6507075M2405053<<<<<<<<<<<<<<00"),
]

# Run test cases
for i, (mrl1, mrl2) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    passport_info = parse_mrz(mrl1, mrl2)
    for key, value in passport_info.items():
        print(f"{key}: {value}")
