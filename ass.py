import logging
from typing import Any, Dict

from fastapi import HTTPException, status
from pydantic import RootModel, field_validator

from exceptions.setup_log import setup_logger
from constant.constants import (
    INVALID_JSON_LOG,
    VALIDATION_SUCCESS_LOG,
    VALIDATION_ERROR_LOG,
    UNEXPECTED_VALIDATION_ERROR_LOG,
    INVALID_JSON_MSG,
    UNEXPECTED_VALIDATION_ERROR_MSG,
)

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception as e:
    logger = None
    print(f"Logger setup failed: {e}")


class FeedbackCreate(RootModel[Dict[str, Any]]):
    """
    Root model for feedback creation.
    Accepts the entire request body as a JSON object.
    No 'content' key is required.
    """

    @field_validator("*", mode="before")
    def validate_content(cls, v):
        """
        Validate that the request body is a proper JSON object (dict).
        Logs success/failure.
        """
        try:
            if not isinstance(v, dict):
                if logger:
                    logger.error(INVALID_JSON_LOG)
                raise ValueError(INVALID_JSON_MSG)

            if logger:
                logger.info(VALIDATION_SUCCESS_LOG)
            return v

        except ValueError as e:
            if logger:
                logger.error(VALIDATION_ERROR_LOG.format(e))
            raise

        except Exception as e:
            if logger:
                logger.error(UNEXPECTED_VALIDATION_ERROR_LOG.format(str(e)))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e)),
            )


class FeedbackResponse(RootModel):
    """
    Response model for feedback data.
    Maps ORM table columns to response fields.
    """

    id: int
    application_id: str
    correlation_id: str
    content: Dict[str, Any]
    soeid: str
    authorization_coin_id: str
    created_at: Any

import logging
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database

from models import models
from db.database import engine, get_db, DB_NAME
from service.schemas import FeedbackCreate
from exceptions.setup_log import setup_logger
from constant.constants import *

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception as e:
    print(f"Logger setup failed: {e}")
    logger = logging.getLogger(__name__)

# ---------------- FastAPI Initialization ----------------
app = FastAPI(title="Feedback API")


@app.on_event("startup")
def create_db_and_tables():
    """
    FastAPI startup event.
    Creates the database and tables if they don't exist.
    """
    try:
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info(DB_CREATED.format(DB_NAME))

        models.Base.metadata.create_all(bind=engine)
        logger.info(DB_TABLES_CREATED)
    except Exception as e:
        logger.error(DB_INIT_FAILURE.format(e))
        raise RuntimeError(DB_INIT_FAILURE_RUNTIME) from e


@app.post("/feedback/", status_code=201)
async def upload_feedback(
    feedback_data: FeedbackCreate,
    x_correlation_id: str = Header(..., alias="x-correlation-id"),
    x_application_id: str = Header(..., alias="x-application-id"),
    x_soeid: str = Header(..., alias="x-soeid"),
    x_authorization_coin: str = Header(..., alias="x-authorization-coin"),
    db: Session = Depends(get_db)
):
    """
    Endpoint to upload feedback.
    Stores entire request body in 'content' column and other fields from headers.
    """
    try:
        payload = feedback_data.model_dump()  # Pydantic v2: get dict from RootModel

        db_feedback = models.Feedback(
            application_id=x_application_id,
            correlation_id=x_correlation_id,
            content=payload,  # Full JSON body
            soeid=x_soeid,
            authorization_coin_id=x_authorization_coin
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        logger.info(f"Feedback stored successfully with ID {db_feedback.id}")

        return {
            "message": "Feedback stored successfully",
            "id": db_feedback.id,
            "application_id": db_feedback.application_id,
            "correlation_id": db_feedback.correlation_id,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"DB operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")


# ---------------- Main Entry Point ----------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
