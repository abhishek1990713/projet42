import requests
import json

# ---------------- Endpoint ----------------
URL = "http://127.0.0.1:8000/upload_json"  # FastAPI running locally on port 8000

# ---------------- Headers ----------------
HEADERS = {
    "x-correlation-id": "test-corr-001",
    "x-application-id": "test-app-001",
    "x-soeid": "user-123",
    "X-Authorization-Coin": "coin-sample",
    "Content-Type": "application/json"
}

# ---------------- Sample JSON Payload ----------------
PAYLOAD = {
    "extractedData": {
        "Bo_Name": "Brazilian Palm Tree LTD",
        "Country_of_residence": "Norway",
        "Pay_Year": 2025,
        "Market": "Finland",
        "Address": "0107 OSLO, NORWAY",
        "law_Article": "Article 4 paragraph 1 of the Tax Convention",
        "Signature": "SIGMOM",
        "Seal": "The Norwegian Tax Admin",
        "Our_Reference": "2024/5570364",
        "Tax_Identification_number": "974761076",
        "BOID_extraction": "",
        "AddressExtraction": "",
        "MTD_SafekeepingAccounts": "",
        "postal_address": "P.O. Box 9200 Grenland 0134 Oslo",
        "Document_Validation": ""
    },
    "feedback": {
        "Bo_Name": {"status": "thumbs_up"},
        "Country_of_residence": {"status": "thumbs_down", "comments": "wfefngn"},
        "Pay_Year": {"status": "thumbs_down", "comments": "th"},
        "Market": {"status": "thumbs_down", "comments": "tnthth"}
    }
}

# ---------------- Send POST Request ----------------
try:
    response = requests.post(URL, headers=HEADERS, json=PAYLOAD)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:", json.dumps(response.json(), indent=4))
except Exception as e:
    print(f"Error during request: {e}")
