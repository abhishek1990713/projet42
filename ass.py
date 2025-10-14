document_stats.py

This module calculates document-level accuracy statistics for a specific 
application_id within a given date range (start_date and end_date).

📘 Description:
----------------
The function `document_stats()` retrieves feedback records for a given 
application_id and date range. For each document, it calculates the 
document-wise accuracy percentage based on field-level thumbs-up and thumbs-down 
feedback.

✅ Formula (in words):
----------------------
For each document:
    Document Accuracy (%) = (Total Thumbs-Up Fields / Total Feedback Fields) × 100

The function then counts how many documents fall into each accuracy range:
- Greater than 81%
- Between 71% and 80%
- Between 50% and 70%
- Less than 50%

Finally, it returns a structured summary showing:
- Application ID
Finally, it returns a structured summary showing:
- Application ID
- Date range used
- Total number of documents
- Count of documents in each accuracy range
""


"""
feedback_report.py

This module generates a feedback accuracy report for a specific `application_id` 
within a given date range (start_date and end_date).

📘 Description:
----------------
The function `feedback_report()` fetches all feedback entries from the database 
for a specific application and calculates field-level accuracy.

Each feedback record contains multiple fields, each having a `status` 
(either "thumbs_up" or "thumbs_down").

✅ Formula (explained in words):
--------------------------------
Field-Level Accuracy (%) = (Number of Thumbs-Up for the field / Total Feedback Count for the field) × 100

Example:
If for the field "Address", there are 8 thumbs_up and 2 thumbs_down,
then accuracy = (8 / 10) × 100 = 80%.

The function finally returns a structured response containing:
- Application ID
- Each field name
- Field-Level Accuracy (%)
- Field-Level Document Count
"""



"""
====================================================================================
File Name: main.py
Description:
-------------
This FastAPI application serves as the backend for managing and analyzing feedback 
data received from the frontend. It performs the following key operations:

1. Receives feedback data for each document, including detailed field-level feedback 
   (thumbs_up / thumbs_down) from users.

2. Calculates important feedback metrics such as:
   - Total number of feedback fields (field_count)
   - Number of positive feedback (thumbs_up_count)
   - Number of negative feedback (thumbs_down_count)
   - Document-wise average accuracy (docswise_avg_accuracy)

3. Stores the feedback records in the database along with metadata such as 
   correlation_id, application_id, document_id, file_name, and timestamps.

4. Provides APIs to:
   - Insert new feedback entries (`/feedback_service`)
   - Generate aggregated reports combining high-level document statistics 
     and detailed field-level feedback (`/aggregated_report`)

------------------------------------------------------------------------------------
Formula Explanation:
--------------------
1️⃣ **Field Count**
   field_count = Number of fields having a feedback status ("thumbs_up" or "thumbs_down")

2️⃣ **Positive Feedback Count**
   thumbs_up_count = Number of fields with status = "thumbs_up"

3️⃣ **Negative Feedback Count**
   thumbs_down_count = Number of fields with status = "thumbs_down"

4️⃣ **Document-Wise Average Accuracy**
   docswise_avg_accuracy = (thumbs_up_count / field_count) * 100

------------------------------------------------------------------------------------
Example:
---------
If a document has 10 fields reviewed and 8 of them are marked as "thumbs_up",
then:

  field_count = 10
  thumbs_up_count = 8
  thumbs_down_count = 2
  docswise_avg_accuracy = (8 / 10) * 100 = 80%

Hence, this document's accuracy will be considered “Good” (based on threshold logic).

------------------------------------------------------------------------------------
Logging & Error Handling:
-------------------------
✅ All exceptions are captured using structured logging via `setup_logger`.
✅ Database operations are logged for insertions and failures.
✅ Validation errors raise HTTP 400 responses with clear messages.
✅ Any unexpected errors are handled gracefully with HTTP 500 responses.

====================================================================================
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Header, status, Query, Body
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Feedback
from service import schemas
from exceptions.setup_log import setup_logger
from constant.constants import *
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime
from service.schemas import HighLevelResponse
import pandas as pd
from document_stats import get_document_percentage_stats
from feedback_report import feedback_report


# -------------------------------------------------------------------------------
# Logger Setup
# -------------------------------------------------------------------------------
try:
    logger = setup_logger()
except Exception:
    logger = None


# -------------------------------------------------------------------------------
# FastAPI Application Setup
# -------------------------------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------------------
# Function: calculate_feedback_stats
# Description:
# This function calculates key feedback metrics for a single document.
# -------------------------------------------------------------------------------
def calculate_feedback_stats(feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate field_count, positive_count, negative_count, and percentage.
    Formula:
        docswise_avg_accuracy = (positive_count / field_count) * 100
    """
    positive_count = 0
    negative_count = 0
    field_count = 0

    for field, data in feedback.items():
        if isinstance(data, dict) and "status" in data:
            field_count += 1
            if data["status"] == "thumbs_up":
                positive_count += 1
            elif data["status"] == "thumbs_down":
                negative_count += 1

    docswise_avg_accuracy = round((positive_count / field_count) * 100, 2) if field_count else 0.0

    return {
        "field_count": field_count,
        "feedback_count": field_count,
        "thumbs_up_count": positive_count,
        "thumbs_down_count": negative_count,
        "docswise_avg_accuracy": docswise_avg_accuracy,
    }

# -------------------------------------------------------------------------------
# POST Endpoint: /feedback_service
# Description:
# Accepts JSON feedback input, calculates metrics, stores in DB, and logs all actions.
# -------------------------------------------------------------------------------
@app.post("/feedback_service", status_code=status.HTTP_201_CREATED)
async def upload_json(
    request: Request,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    x_correlation_id: str = Header(...),
    x_application_id: str = Header(...),
    x_created_by: str = Header(...),
    x_document_id: str = Header(...),
    x_file_id: str = Header(...),
    x_authorization_coin: str = Header(...),
    x_feedback_source: str = Header(...)
):
    try:
        document_type = payload.get("Document_type", "Unknown")
        feedback_section = payload.get("field_feedback", {})
        stats = calculate_feedback_stats(feedback_section)

        feedback_data = schemas.FeedbackResponse(
            feedback_id=0,
            correlation_id=x_correlation_id,
            application_id=x_application_id,
            document_id=x_document_id,
            file_name=x_file_id,
            authorization_coin_id=x_authorization_coin,
            feedback_response=payload,
            feedback_source=x_feedback_source,
            created_by=x_created_by,
            created_on=datetime.now(),
            feedback_count=stats.get("feedback_count", 0),
            thumbs_up_count=stats.get("thumbs_up_count", 0),
            thumbs_down_count=stats.get("thumbs_down_count", 0),
            docswise_avg_accuracy=stats.get("docswise_avg_accuracy", 0.0),
            document_type=document_type
        )

    except Exception as e:
        if logger:
            logger.error(VALIDATION_ERROR_LOG.format(e), exc_info=True)
        raise HTTPException(status_code=400, detail=VALIDATION_FAILED_MSG)

    try:
        db_feedback = Feedback(
            correlation_id=x_correlation_id,
            created_by=x_created_by,
            application_id=x_application_id,
            document_id=x_document_id,
            file_name=x_file_id,
            authorization_coin_id=x_authorization_coin,
            feedback_source=x_feedback_source,
            feedback_response=payload,
            feedback_count=stats["feedback_count"],
            thumbs_up_count=stats["thumbs_up_count"],
            thumbs_down_count=stats["thumbs_down_count"],
            docswise_avg_accuracy=stats["docswise_avg_accuracy"],
            document_type=document_type
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        if logger:
            logger.info(DB_INSERT_SUCCESS_LOG)

        return {
            "message": DATA_INSERTED,
            SUCCESS: True,
