"""
main.py

This FastAPI application handles feedback submission and generates
aggregated reports (high-level and field-level) for a given application_id.

📘 Endpoints:
1. /feedback_service      → Insert new feedback data
2. /aggregated_report     → Generate combined high-level and field-level reports

High-level report uses:
    → get_document_percentage_stats(application_id, start_date, end_date)

Field-level report uses:
    → feedback_report(application_id, start_date, end_date)
"""

from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    Depends,
    Header,
    status,
    Query,
    Body
)
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Feedback
from exceptions.setup_log import setup_logger
from constant.constants import *
from document_stats import get_document_percentage_stats
from feedback_report import feedback_report
from datetime import datetime
from typing import Dict, Any
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Logger setup
try:
    logger = setup_logger()
except Exception:
    logger = None

app = FastAPI(title="Feedback Analytics API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Utility Function
# ---------------------------------------------------------------------
def calculate_feedback_stats(feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate field count, thumbs up/down counts, and document-wise accuracy.

    Formula:
    Document Accuracy (%) = (Thumbs-Up Fields / Total Fields) × 100
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
        "docswise_avg_accuracy": docswise_avg_accuracy
    }

# ---------------------------------------------------------------------
# POST Endpoint — Insert Feedback
# ---------------------------------------------------------------------
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
    x_feedback_source: str = Header(...),
):
    """
    Accepts feedback JSON and stores it in the database with computed stats.
    """
    try:
        document_type = payload.get("Document_type", "Unknown")
        feedback_section = payload.get("field_feedback", {})

        stats = calculate_feedback_stats(feedback_section)

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
            document_type=document_type,
            created_on=datetime.now()
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        if logger:
            logger.info(DB_INSERT_SUCCESS_LOG)

        return {
            "message": DATA_INSERTED,
            "success": True,
            "details": {
                "feedback_id": db_feedback.feedback_id,
                "correlation_id": db_feedback.correlation_id,
                "application_id": db_feedback.application_id,
                "created_by": db_feedback.created_by,
                "document_id": db_feedback.document_id,
                "feedback_source": db_feedback.feedback_source,
                "file_name": db_feedback.file_name,
                "feedback_count": db_feedback.feedback_count,
                "thumbs_up_count": db_feedback.thumbs_up_count,
                "thumbs_down_count": db_feedback.thumbs_down_count,
                "docswise_avg_accuracy": db_feedback.docswise_avg_accuracy
            }
        }

    except Exception as e:
        db.rollback()
        if logger:
            logger.error(DB_OPERATION_FAILED_LOG.format(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------
# GET Endpoint — Aggregated Report
# ---------------------------------------------------------------------
@app.get("/aggregated_report", tags=["Aggregated Report"])
def fetch_combined_report(
    application_id: str = Header(...),
    start_date: str = Query(..., description="Start date in format YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in format YYYY-MM-DD")
):
    """
    Fetch combined high-level and field-level feedback reports.

    Combines:
      - High-level (document accuracy distribution)
      - Field-level (field accuracy per field)
    """
    try:
        if not application_id or not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail="Headers 'application_id', 'start_date', and 'end_date' are required."
            )

        logger.info(
            f"Received request for application_id={application_id}, start_date={start_date}, end_date={end_date}"
        )

        # Fetch high-level stats
        high_level_result = get_document_percentage_stats(application_id, start_date, end_date)
        if not high_level_result or (isinstance(high_level_result, dict) and "error" in high_level_result):
            raise HTTPException(status_code=404, detail=f"No high-level records found for application_id={application_id}")

        # Fetch detailed feedback report
        feedback_result = feedback_report(application_id, start_date, end_date)
        if not feedback_result or (isinstance(feedback_result, dict) and "error" in feedback_result):
            raise HTTPException(status_code=404, detail=f"No feedback report found for application_id={application_id}")

        # Combine both results
        combined_reports = [
            {"report_type": "high_level", **high_level_result[0]},
            {"report_type": "field_level", **feedback_result[0]}
        ]

        return combined_reports

    except HTTPException as http_err:
        logger.warning(f"HTTP error in combined report: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error in fetch_combined_report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------------------------------------------------------
# Run the Server
# ---------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

