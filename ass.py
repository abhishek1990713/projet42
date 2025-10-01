import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Replace these with actual values from your DB for testing
TEST_APPLICATION_ID = "test_app_1"
TEST_DOCUMENT_ID = "test_doc_1"
VALID_START_DATE = "2025-09-01"
VALID_END_DATE = "2025-09-30"
INVALID_DATE = "2025-13-01"  # Invalid month


def test_fetch_feedback_success():
    """Test fetching feedback successfully"""
    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": TEST_APPLICATION_ID,
            "document_id": TEST_DOCUMENT_ID,
            "start_day": VALID_START_DATE,
            "end_day": VALID_END_DATE,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        data = response.json()[0]
        expected_keys = ["id", "correlation_id", "application_id", "soeid",
                         "authorization_coin_id", "document_id", "file_id",
                         "feedback_json", "created_at"]
        for key in expected_keys:
            assert key in data


def test_fetch_feedback_invalid_date():
    """Test API with invalid date format"""
    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": TEST_APPLICATION_ID,
            "document_id": TEST_DOCUMENT_ID,
            "start_day": INVALID_DATE,
            "end_day": VALID_END_DATE,
        },
    )
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]


def test_fetch_feedback_no_records():
    """Test API when no records exist for given parameters"""
    response = client.get(
        "/fetch_feedback",
        params={
            "application_id": "nonexistent_app",
            "document_id": "nonexistent_doc",
            "start_day": VALID_START_DATE,
            "end_day": VALID_END_DATE,
        },
    )
    assert response.status_code == 404
    assert "No records found" in response.json()["detail"]


def test_fetch_feedback_missing_params():
    """Test API with missing required parameters"""
    response = client.get("/fetch_feedback")
    assert response.status_code == 422  # FastAPI validation error



from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from models.models import Feedback
from db.database import get_db
from exceptions.setup_log import setup_logger
from schemas.schemas import FeedbackResponse
import uvicorn

# Logger Setup
try:
    logger = setup_logger()
except Exception as e:
    print(f"Logger initialization failed: {e}")
    logger = None

# FastAPI App
app = FastAPI(title="Feedback API", version="1.0")


@app.get("/fetch_feedback", response_model=List[FeedbackResponse])
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    document_id: str = Query(..., description="Document ID"),
    start_day: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_day: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    """
    Fetch feedback records for a given application_id and document_id within a date range.
    Returns a list of feedback records.
    """
    try:
        # Validate date format
        try:
            datetime.strptime(start_day, "%Y-%m-%d")
            datetime.strptime(end_day, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        start_datetime = f"{start_day} 00:00:00"
        end_datetime = f"{end_day} 23:59:59"

        # Query Feedback table
        results = (
            db.query(Feedback)
            .filter(Feedback.application_id == application_id)
            .filter(Feedback.document_id == document_id)
            .filter(Feedback.created_at.between(start_datetime, end_datetime))
            .order_by(Feedback.id.asc())
            .all()
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No records found for the given application_id, document_id, and date range",
            )

        if logger:
            logger.info(f"Fetched {len(results)} feedback records for app_id={application_id}, doc_id={document_id}")

        return results

    except HTTPException:
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error fetching feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Run Server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
