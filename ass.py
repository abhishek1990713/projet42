
import requests

def test_upload_json_file():
    """
    Test script to upload an existing JSON file to the FastAPI API.
    """
    url = "http://127.0.0.1:9000/upload-json/"  # API endpoint

    # Replace with your actual JSON file name
    json_file_path = "input.json"

    # Open and send JSON file
    with open(json_file_path, "rb") as f:
        files = {"file": (json_file_path, f, "application/json")}
        response = requests.post(url, files=files)

    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except Exception:
        print("Raw Response:", response.text)


if __name__ == "__main__":
    test_upload_json_file()
