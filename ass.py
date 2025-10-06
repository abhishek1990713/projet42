from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict

from models.models import Feedback
from db.database import get_db
from exceptions.setup_log import setup_logger
import uvicorn
import logging


# Logger Setup
try:
    logger = setup_logger()
except Exception:
    logger = logging.getLogger("feedback_api")
    logging.basicConfig(level=logging.INFO)


app = FastAPI(title="Feedback API", version="1.0")


# Helper Function: Parse Date
def parse_date(date_str: str) -> datetime:
    """Parse string date in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")


# Endpoint to fetch only specific columns
@app.get("/fetch_feedback")
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    document_id: str = Query(..., description="Document ID"),
    start_day: str = Query(..., description="Date in YYYY-MM-DD format"),
    end_day: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    """Fetch only selected columns for a given application_id and document_id within a date range"""

    try:
        # Validate and parse dates
        start_date = parse_date(start_day)
        end_date = parse_date(end_day)

        start_datetime = f"{start_date.strftime('%Y-%m-%d')} 00:00:00"
        end_datetime = f"{end_date.strftime('%Y-%m-%d')} 23:59:59"

        # Query only specific columns
        results = (
            db.query(
                Feedback.id,
                Feedback.correlation_id,
                Feedback.application_id,
                Feedback.document_id,
                Feedback.file_id,
            )
            .filter(Feedback.application_id == application_id)
            .filter(Feedback.document_id == document_id)
            .filter(Feedback.created_at.between(start_datetime, end_datetime))
            .order_by(Feedback.id.asc())
            .all()
        )

        # Convert SQLAlchemy Row objects to dictionaries
        response_data: List[Dict] = [
            {
                "id": row.id,
                "correlation_id": row.correlation_id,
                "application_id": row.application_id,
                "document_id": row.document_id,
                "file_id": row.file_id,
            }
            for row in results
        ]

        if logger:
            logger.info(
                f"Fetched {len(response_data)} feedback records for app_id={application_id}, doc_id={document_id}"
            )

        return response_data

    except Exception as e:
        if logger:
            logger.error(f"Error fetching feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
