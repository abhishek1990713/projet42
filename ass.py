import re
import pandas as pd
import pycountry

# Load UN/LOCODE CSV (download from UNECE site)
# File should have columns: Country, Location, Name
df = pd.read_csv("unlocode.csv")
df['LOCODE'] = df['Country'] + df['Location']
VALID_PORT_CODES = set(df['LOCODE'])

# Set of valid country codes
COUNTRY_CODES = {country.alpha_2 for country in pycountry.countries}

def find_real_port_codes(text):
    pattern = r'\b([A-Z]{2})([A-Z0-9]{3})\b'
    matches = re.findall(pattern, text)

    valid = []
    for country, location in matches:
        code = country + location
        if country in COUNTRY_CODES and code in VALID_PORT_CODES:
            valid.append(code)
    return valid

sample_text = """
Shipment from INNSA to USNYC via JPTYO.
Also check SABIC, MARKS, TOTAL.
"""
print(find_real_port_codes(sample_text))
