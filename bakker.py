def extract_dob_from_mrz_line(second_line):
    if len(second_line) < 20:
        return None  # Line is too short to contain a DOB

    dob_raw = second_line[13:19]  # MRZ index starts at 0
    year = dob_raw[:2]
    month = dob_raw[2:4]
    day = dob_raw[4:6]

    # Handle century guessing (assuming 1900–2099 range)
    current_year = int(str(year))
    century = "20" if int(year) <= 30 else "19"  # You can adjust the threshold
    full_year = century + year

    return f"{full_year}-{month}-{day}"
second_line = "8262320915USA6063179F1955876940<774852"
dob = extract_dob_from_mrz_line(second_line)
print("Date of Birth:", dob)
