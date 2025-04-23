

def extract_dob_from_mrz_line(second_line):
    if len(second_line) < 20:
        return None  # Line too short to contain DOB

    dob_raw = second_line[13:19]  # Positions 14–19 in MRZ are for DOB: YYMMDD

    year = dob_raw[:2]
    month = dob_raw[2:4]
    day = dob_raw[4:6]

    # Guess century: if year >= 30 → 1900s, else 2000s
    try:
        full_year = int(year)
        century = "19" if full_year > 30 else "20"
        full_year_str = century + year
    except ValueError:
        return None  # In case the year is not digits

    return f"{full_year_str}-{month}-{day}"
