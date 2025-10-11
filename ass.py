Perfect 👍 — you already have a clean, production-style FastAPI setup for your **feedback service** and **document statistics** APIs.

Below is a **detailed documentation** of the **entire workflow**, including:

* Functional overview
* Input/output formats
* API endpoints with request/response samples
* Flow diagram
* Database details
* Error handling

---

# 📘 **Project Documentation — Feedback Service & Document Statistics**

---

## 🧩 **1. Overview**

This service provides:

* A **Feedback API** that accepts structured feedback JSON data and stores it in a PostgreSQL database.
* A **Statistics API** that computes percentage-based performance metrics (positive/negative feedback ratio) by `document_type`.

The project uses:

* **FastAPI** for the REST APIs
* **SQLAlchemy ORM** for database operations
* **Pydantic** for input validation
* **PostgreSQL** with `JSONB` for feedback storage
* **Logger** for structured logging

---

## ⚙️ **2. Core Workflow**

### Step-by-Step Data Flow:

1. **User submits a feedback JSON** to `/feedback_service` (POST).
2. The backend extracts:

   * `Document_type` from payload.
   * Feedback stats (`thumbs_up`, `thumbs_down`, etc.).
3. The service calculates:

   * Total fields (`field_count`)
   * Positive and negative counts
   * Positive percentage = `(positive_count / total_fields) × 100`
4. Data is inserted into the `feedback` table in PostgreSQL.
5. The `/document_stats` GET API returns aggregated statistics by `document_type`.
6. The `/document_types` GET API lists all available document types.

---

## 🗂️ **3. Database Design**

### **Table Name:**

`gssp_common.feedback`  *(as per `GSSP_SCHEMA` and `TABLE_NAME` constants)*

### **Schema:**

| Column Name           | Type      | Description                                 |
| --------------------- | --------- | ------------------------------------------- |
| id                    | INT (PK)  | Auto-generated ID                           |
| correlation_id        | TEXT      | Request tracking ID                         |
| application_id        | TEXT      | Application identifier                      |
| document_id           | TEXT      | Unique document identifier                  |
| file_id               | TEXT      | Unique file identifier                      |
| authorization_coin_id | TEXT      | Authorization token ID                      |
| feedback_response     | JSONB     | Raw feedback payload                        |
| feedback_source       | TEXT      | Feedback origin (API/UI)                    |
| created_by            | TEXT      | User who created feedback                   |
| created_on            | TIMESTAMP | Timestamp (auto-generated)                  |
| document_type         | TEXT      | Document category (e.g., passport, license) |
| field_count           | INT       | Total feedback fields                       |
| positive_count        | INT       | Count of thumbs_up                          |
| negative_count        | INT       | Count of thumbs_down                        |
| percentage            | FLOAT     | Positive feedback %                         |

---

## 🧾 **4. API Endpoints**

---

### 🟢 **A. POST /feedback_service**

#### **Purpose**

Insert feedback data into the database with calculated statistics.

#### **Headers**

| Header Name            | Description                 |
| ---------------------- | --------------------------- |
| `x-correlation-id`     | Unique ID for tracking      |
| `x-application-id`     | Application identifier      |
| `x-created-by`         | Creator username            |
| `x-document-id`        | Document ID                 |
| `x-file-id`            | File ID                     |
| `x-authorization-coin` | Authorization token         |
| `x-feedback-source`    | Source of feedback (UI/API) |

#### **Request Body (JSON)**

```json
{
  "Document_type": "passport",
  "extractedData": {
    "Name": "John Doe",
    "Country": "Japan"
  },
  "feedback": {
    "Name": {"status": "thumbs_up"},
    "Country": {"status": "thumbs_down", "comments": "Mismatch with passport"}
  }
}
```

#### **Processing Logic**

* Extract `Document_type` from payload.
* Count:

  * `field_count` = total fields in `feedback`.
  * `positive_count` = number of `thumbs_up`.
  * `negative_count` = number of `thumbs_down`.
* Compute:

  * `percentage = (positive_count / field_count) * 100`.
* Insert record in database.

#### **Response**

```json
{
  "message": "Data inserted successfully",
  "success": true,
  "details": {
    "id": 102,
    "correlation_id": "corr-001",
    "application_id": "app-789",
    "created_by": "akshya",
    "document_id": "DOC001",
    "feedback_source": "UI",
    "file_id": "FILE001",
    "document_type": "passport",
    "field_count": 2,
    "positive_count": 1,
    "negative_count": 1,
    "percentage": 50.0
  }
}
```

---

### 🟣 **B. GET /document_stats**

#### **Purpose**

Retrieve feedback statistics for a given `document_type`.

#### **Header**

| Header Name     | Description                                                          | Required |
| --------------- | -------------------------------------------------------------------- | -------- |
| `document_type` | Type of document to filter (e.g., passport, license, bill_of_lading) | ✅ Yes    |

#### **Response Example**

```json
[
  {
    "document_type": "passport",
    "total_documents": 25,
    "greater_than_81": 10,
    "range_71_to_80": 6,
    "range_50_to_70": 7,
    "less_than_50": 2,
    "summary_percentage": {
      ">81%": 40.0,
      "71–80%": 24.0,
      "50–70%": 28.0,
      "<50%": 8.0
    }
  }
]
```

#### **Logic**

* If `document_type` is passed → filter by that type.
* Else → return stats for all available document types.
* Uses SQL `CASE` conditions to compute distribution ranges:

  * `>81%`
  * `71–80%`
  * `50–70%`
  * `<50%`

---

### 🔵 **C. GET /document_types**

#### **Purpose**

Fetch all distinct `document_type` values from the feedback table.

#### **Response Example**

```json
[
  "passport",
  "driving_license",
  "bill_of_lading",
  "residence_certificate"
]
```

---

## 🔁 **5. Full Process Flow Diagram**

```text
               ┌────────────────────────────┐
               │  Client Application (UI)  │
               └────────────┬──────────────┘
                            │
                            ▼
               ┌────────────────────────────┐
               │  POST /feedback_service     │
               │  (Feedback Submission API)  │
               └────────────┬──────────────┘
                            │
                            ▼
          ┌──────────────────────────────────────────┐
          │ Extract "Document_type" & feedback stats  │
          │ field_count, positive_count, percentage   │
          └────────────────┬─────────────────────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │  PostgreSQL (feedback)   │
              │  Insert structured data  │
              └────────────┬─────────────┘
                            │
                            ▼
       ┌────────────────────────────┐      ┌────────────────────────────┐
       │ GET /document_stats        │      │ GET /document_types        │
       │ Calculate stats by type    │      │ Fetch distinct types       │
       └────────────────────────────┘      └────────────────────────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │ JSON Response to Client  │
              └──────────────────────────┘
```

---

## ⚠️ **6. Error Handling**

| Error Type                | Example Message                                   | Cause                      |
| ------------------------- | ------------------------------------------------- | -------------------------- |
| 400 Bad Request           | `"Validation failed: Missing field"`              | Invalid input JSON         |
| 404 Not Found             | `"No records found for given document type"`      | No data for requested type |
| 500 Internal Server Error | `"Database operation failed: connection timeout"` | DB/ORM failure             |

---

## 🪵 **7. Logging**

All logs go through `logger_config.py`.

**Examples:**

```
INFO  - [main.py] Fetching document percentage statistics...
INFO  - [main.py] Inserted feedback record for document_type: passport
ERROR - [document_stats.py] Error in get_document_percentage_stats: division by zero
```

---

## 🧮 **8. Key Computation Formula**

```python
field_count = len(feedback.keys())
positive_count = sum(1 for v in feedback.values() if v["status"] == "thumbs_up")
negative_count = sum(1 for v in feedback.values() if v["status"] == "thumbs_down")
percentage = (positive_count / field_count) * 100 if field_count > 0 else 0
```

---

## ✅ **9. Summary**

| Functionality      | API                      | Description                             |
| ------------------ | ------------------------ | --------------------------------------- |
| Insert Feedback    | `POST /feedback_service` | Stores feedback with calculated metrics |
| Document Stats     | `GET /document_stats`    | Retrieves summary by `document_type`    |
| All Document Types | `GET /document_types`    | Lists all unique document types in DB   |

---

Would you like me to create a **PDF version** of this documentation (with clean formatting and section headers) so you can share it or attach it to your project?
