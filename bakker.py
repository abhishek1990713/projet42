import re

def parse_mrz(mrl1, mrl2):
    # Extract relevant information from the MRZ lines
    
    # Line 1
    country_code = mrl1[2:5]  # Issuing country
    surname, given_names = re.split('<+', mrl1[5:].split('<<', 1)[0])  # Names
    
    # Line 2
    passport_number = mrl2[:9]  # Passport number
    nationality = mrl2[10:13]   # Nationality
    dob = f"{mrl2[13:15]}/{mrl2[15:17]}/{mrl2[17:19]}"  # Date of birth (YYMMDD)
    gender = 'Male' if mrl2[20] == 'M' else 'Female' if mrl2[20] == 'F' else 'Unspecified'
    expiry_date = f"{mrl2[21:23]}/{mrl2[23:25]}/{mrl2[25:27]}"  # Expiry date (YYMMDD)
    
    extracted_info = {
        "Issuing Country": country_code,
        "Surname": surname,
        "Given Names": given_names.replace('<', ' '),
        "Passport Number": passport_number,
        "Nationality": nationality,
        "Date of Birth": dob,
        "Gender": gender,
        "Expiry Date": expiry_date,
    }
    
    return extracted_info

# Example Inputs
mrl1 = "P<GBRANGUILLA<SPECIMEN<<ANGELA<ZOE<<<<<<<<<<"
mrl2 = "9992026018GBD9501016F2911272<<<<<<<<<<<<<<00"

# Extract Information
passport_info = parse_mrz(mrl1, mrl2)

# Print Output
for key, value in passport_info.items():
    print(f"{key}: {value}")

P<RUSSMIRNOVA<<VALENTINA

<<<<<<<

5200000001RUS8008046F0902274<<<<<<<<<<<<<<06
