
# main.py

import json
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, Header, Request
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database

from models import models
from db.database import engine, get_db, DB_NAME
from service.schemes import FeedbackCreate, INVALID_JSON_MSG
from exceptions.setup_log import setup_logger
from constant.constants import *

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception as e:
    print(f"Logger setup failed: {e}")
    logger = None

# ---------------- FastAPI Initialization ----------------
app = FastAPI(title="Feedback API")


@app.on_event("startup")
def create_db_and_tables():
    """
    Event handler for FastAPI startup.
    Creates the database (if it doesn't exist) and initializes all tables.
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


@app.post(UPLOAD_JSON, status_code=status.HTTP_201_CREATED)
async def upload_json(
    request: Request,
    x_correlation_id: str = Header(...),
    x_application_id: str = Header(...),
    x_soeid: str = Header(...),
    x_authorization_coin: str = Header(...),
    content_type: str = Header(..., alias="Content-Type"),
    db: Session = Depends(get_db)
):
    """
    Endpoint to upload feedback JSON with headers providing metadata.
    """
    # Validate Content-Type
    if content_type.lower() != "application/json":
        logger.warning(f"Invalid Content-Type: {content_type}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content-Type must be application/json"
        )

    if not x_authorization_coin:
        logger.warning(MISSING_AUTH_COIN_ID_LOG)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=MISSING_AUTH_COIN_ID_ERROR
        )

    try:
        # Read JSON body
        feedback_data_json = await request.json()
        logger.info(FILE_PARSED_AS_JSON)

        # Create Pydantic object with header values + JSON
        feedback_data = FeedbackCreate(
            application_id=x_application_id,
            consumer_id=x_soeid,
            feedback_json=feedback_data_json
        )
        logger.info(JSON_VALIDATION_SUCCESS)

        # Store in database
        db_feedback = models.Feedback(
            application_id=feedback_data.application_id,
            consumer_id=feedback_data.consumer_id,
            authorization_coin_id=x_authorization_coin,
            feedback_json=feedback_data.feedback_json
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        logger.info(DB_INSERT_SUCCESS_LOG)

        return {
            SUCCESS: True,
            MESSAGE: DATA_INSERTED,
            DETAILS: {
                "id": db_feedback.id,
                "table": models.TABLE_NAME,
                "application_id": db_feedback.application_id,
                "consumer_id": db_feedback.consumer_id,
                "correlation_id": x_correlation_id
            }
        }

    except json.JSONDecodeError:
        logger.error(INVALID_JSON_LOG)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_JSON_MSG
        )
    except Exception as e:
        db.rollback()
        logger.error(DB_OPERATION_FAILED_LOG.format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR_MSG.format(str(e))
        )


# ---------------- Main Entry Point ----------------
if __name__ == "__main__":
    uvicorn.run(
        UVICORN_APP,
        host=UVICORN_HOST,
        port=UVICORN_PORT,
        log_level=UVICORN_LOG_LEVEL,
        reload=UVICORN_RELOAD
    )
