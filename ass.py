from fastapi import FastAPI, Request, HTTPException, Depends, Header, status, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import uvicorn

from db.database import get_db
from models.models import Feedback
from service import schemas
from exceptions.setup_log import setup_logger
from constant.constants import (
    VALIDATION_SUCCESS_LOG,
    VALIDATION_ERROR_LOG,
    VALIDATION_FAILED_MSG,
    DB_INSERT_SUCCESS_LOG,
    DB_OPERATION_FAILED_LOG,
    UNEXPECTED_VALIDATION_ERROR_MSG,
    DATA_INSERTED,
    SUCCESS
)


# -----------------------------------------------------------
# Logger setup
# -----------------------------------------------------------
try:
    logger = setup_logger()
except Exception:
    logger = None


# -----------------------------------------------------------
# FastAPI app initialization
# -----------------------------------------------------------
app = FastAPI(title="Feedback Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------
# Utility: Calculate field stats
# -----------------------------------------------------------
def calculate_feedback_stats(feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate field_count, positive_count, negative_count, and percentage.
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

    percentage = round((positive_count / field_count) * 100, 2) if field_count else 0.0

    return {
        "field_count": field_count,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "percentage": percentage
    }


# -----------------------------------------------------------
# API endpoint: Insert feedback data
# -----------------------------------------------------------
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
    """
    Endpoint to insert feedback data into the database.
    Validates input, calculates feedback stats, and stores JSON feedback.
    """

    # -------------------------------------------------------
    # Step 1: Validate and calculate feedback stats
    # -------------------------------------------------------
    try:
        feedback_section = payload.get("feedback", {})
        stats = calculate_feedback_stats(feedback_section)

        feedback_data = schemas.FeedbackResponse(
            id=0,
            correlation_id=x_correlation_id,
            application_id=x_application_id,
            document_id=x_document_id,
            file_id=x_file_id,
            authorization_coin_id=x_authorization_coin,
            feedback_response=payload,
            feedback_source=x_feedback_source,
            created_by=x_created_by,
            created_on=datetime.now(),
            field_count=stats["field_count"],
            positive_count=stats["positive_count"],
            negative_count=stats["negative_count"],
            percentage=stats["percentage"]
        )

        if logger:
            logger.info(VALIDATION_SUCCESS_LOG)

    except Exception as e:
        if logger:
            logger.error(VALIDATION_ERROR_LOG.format(e), exc_info=True)
        raise HTTPException(status_code=400, detail=VALIDATION_FAILED_MSG)

    # -------------------------------------------------------
    # Step 2: Insert feedback into the database
    # -------------------------------------------------------
    try:
        db_feedback = Feedback(
            correlation_id=x_correlation_id,
            created_by=x_created_by,
            application_id=x_application_id,
            document_id=x_document_id,
            file_id=x_file_id,
            authorization_coin_id=x_authorization_coin,
            feedback_source=x_feedback_source,
            feedback_response=payload,
            field_count=stats["field_count"],
            positive_count=stats["positive_count"],
            negative_count=stats["negative_count"],
            percentage=stats["percentage"]
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        if logger:
            logger.info(DB_INSERT_SUCCESS_LOG)

        return {
            "message": DATA_INSERTED,
            SUCCESS: True,
            "details": {
                "id": db_feedback.id,
                "correlation_id": db_feedback.correlation_id,
                "application_id": db_feedback.application_id,
                "created_by": db_feedback.created_by,
                "document_id": db_feedback.document_id,
                "feedback_source": db_feedback.feedback_source,
                "file_id": db_feedback.file_id,
                "field_count": db_feedback.field_count,
                "positive_count": db_feedback.positive_count,
                "negative_count": db_feedback.negative_count,
                "percentage": db_feedback.percentage
            }
        }

    except Exception as e:
        db.rollback()
        if logger:
            logger.error(DB_OPERATION_FAILED_LOG.format(e), exc_info=True)
        raise HTTPException(status_code=500, detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e)))


# -----------------------------------------------------------
# Run the FastAPI server
# -----------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8092, reload=True)
