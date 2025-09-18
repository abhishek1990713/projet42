Got it 👍 You want a **fully polished client-ready documentation** that you can send directly.
Here’s a **well-structured, professional README/documentation** with all the details properly written, formatted, and explained.

---

# 📘 Feedback API – Documentation

## 1. Overview

The **Feedback API** is a FastAPI-based microservice that allows clients to:

* Upload feedback as JSON files.
* Validate JSON content against required fields.
* Store the feedback into a **PostgreSQL** database.
* Enforce **Authorization Coin ID** from request headers.

This service ensures:
✔️ Automatic database & table creation.
✔️ Data validation using **Pydantic**.
✔️ Clear error handling.
✔️ Ready-to-use **Swagger API docs**.

---

## 2. Technology Stack

* **Python 3.10+**
* **FastAPI** (Web Framework)
* **SQLAlchemy ORM** (Database ORM)
* **PostgreSQL** (Database)
* **Uvicorn** (ASGI server)
* **Pydantic v2** (Validation)

---

## 3. Project Structure

```
project-root/
│── app/
│   ├── database.py       # DB connection, session, role setup
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic schemas for validation
│   ├── main.py           # FastAPI application & endpoints
│── requirements.txt      # Python dependencies
│── README.md             # Documentation (this file)
```

---

## 4. Database Configuration

Update your **PostgreSQL credentials** inside `app/database.py`:

```python
DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USER = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACb"
DB_NAME = "gssp_common"
DB_SESSION_ROLE = "citi_pg_app_owner"
```

The connection string is constructed as:

```
postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>
```

---

## 5. Installation & Setup

### 5.1 Clone the Repository

```bash
git clone <repo-url>
cd project-root
```

### 5.2 Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 5.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 5.4 Run the API Server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload
```

---

## 6. API Documentation

Once the server is running, access interactive docs:

* **Swagger UI** → [http://127.0.0.1:9000/docs](http://127.0.0.1:9000/docs)
* **ReDoc** → [http://127.0.0.1:9000/redoc](http://127.0.0.1:9000/redoc)

---

## 7. API Endpoints

### **POST /upload-json/**

Upload a JSON file and save it into the database.

#### Headers

```http
Authorization-Coin-Id: <string>   # Required
```

#### Request Example (cURL)

```bash
curl -X POST "http://127.0.0.1:9000/upload-json/" \
  -H "Authorization-Coin-Id: sample-auth-123" \
  -F "file=@sample.json"
```

#### Example JSON File (`sample.json`)

```json
{
  "application_id": "APP123",
  "consumer_id": "CNS456",
  "feedback": "The service was excellent!"
}
```

#### Successful Response

```json
{
  "success": true,
  "message": "Data inserted successfully.",
  "details": {
    "id": 1,
    "table": "Feedback",
    "application_id": "APP123",
    "consumer_id": "CNS456"
  }
}
```

---

## 8. Error Handling

The API returns descriptive error messages:

| Status Code | Error Message                                                                |
| ----------- | ---------------------------------------------------------------------------- |
| **400**     | `"Missing Authorization-Coin-Id header"`                                     |
| **400**     | `"Required fields 'application_id' or 'consumer_id' are missing from JSON."` |
| **400**     | `"File is not a valid JSON."`                                                |
| **500**     | `"An unexpected error occurred: <details>"`                                  |

---

## 9. Database Schema

**Schema:** `gssp_common`
**Table:** `Feedback`

| Column                  | Type      | Constraints     |
| ----------------------- | --------- | --------------- |
| id                      | SERIAL    | Primary Key     |
| application\_id         | TEXT      | NOT NULL        |
| consumer\_id            | TEXT      | NOT NULL        |
| authorization\_coin\_id | TEXT      | NOT NULL        |
| feedback\_json          | JSONB     | NOT NULL        |
| created\_at             | TIMESTAMP | Default `NOW()` |

---

## 10. Testing

### Unit Test with Pytest

Create a file `test_main.py`:

```python
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_json_success():
    test_json = {
        "application_id": "APP123",
        "consumer_id": "CNS456",
        "feedback": "All good"
    }
    files = {"file": ("test.json", json.dumps(test_json), "application/json")}
    headers = {"Authorization-Coin-Id": "auth-123"}
    response = client.post("/upload-json/", files=files, headers=headers)
    assert response.status_code == 201
    assert response.json()["success"] is True
```

Run tests:

```bash
pytest -v
```

---

## 11. Logging

Logs are written to the console by default. Example:

```
INFO:root:Database 'gssp_common' created.
INFO:root:Tables created/ensured.
INFO:root:Data inserted successfully.
```

You can extend this by replacing `logging.basicConfig` with a **rotating file logger** in `database.py` or `main.py`.

---

## 12. Deployment

For production:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 4
```

Use a **process manager** like `gunicorn` or `supervisor` and a reverse proxy like **NGINX** for stability.

---

# ✅ Summary

This API provides a **robust and validated pipeline** for uploading and storing feedback JSON in PostgreSQL with role-based DB access, validation, and structured error handling.

---

👉 Would you like me to **convert this into a formal PDF (with headers, tables, and diagrams)** so you can send it as an official delivery document to your client?
