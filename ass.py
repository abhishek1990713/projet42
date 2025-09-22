x_correlation_id: str = Header(..., description="Correlation ID"),
x_application_id: str = Header(..., description="Application ID"),
x_soeid: str = Header(..., description="Consumer SOEID"),
x_authorization_coin: str = Header(..., description="Authorization Coin ID"),

# test_upload_json.py

import requests

API_URL = "http://localhost:8000/upload_json"

# ✅ Corrected headers (use hyphens instead of underscores)
headers = {
    "x-correlation-id": "CORR456",
    "x-application-id": "APP123",
    "x-soeid": "USER789",
    "x-authorization-coin": "COIN101"
}

payload = {
    "content": {
        "extractedData": {
            "Bo_Name": "Brazilian Palm Tree LTD",
            "Country_of_residence": "Norway",
            "Pay Year": 2025,
            "Market": "Finland",
            "Address": "0107 OSLO, NORWAY",
            "law Article": "Article 4 paragraph 1 of the Tax Convention",
            "Signature": "SIGMOM",
            "Seal": "The Norwegian Tax Admin",
            "Our Reference": "2024/5570364",
            "Tax_Identification_number": "974761076",
            "BOID extraction": "",
            "Address Extraction": "",
            "MTD SafekeepingAccounts": "",
            "DepoExtraction": "",
            "Address verification": "",
            "postal address": "P.O. Box 9288 Grenland 0134 Oslo",
            "Document Validation": ""
        },
        "feedback": {
            "Bo Name": {"status": "thumbs_up"},
            "Country_of_residence": {"status": "thumbs_down", "comments": "wfefngn"},
            "Pay Year": {"status": "thumbs_down", "comments": "th"}
        }
    }
}

response = requests.post(API_URL, json=payload, headers=headers)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
