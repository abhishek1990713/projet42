# main.py

import json
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, Header, Request
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database
from pydantic import ValidationError

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
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# ---------------- FastAPI Initialization ----------------
app = FastAPI(title="Feedback API")


@app.on_event("startup")
def create_db_and_tables():
    """
    FastAPI startup event.
    Creates the database if it does not exist and initializes all tables.
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
    x_correlation_id: str = Header(..., description="Correlation ID for tracing requests"),
    x_application_id: str = Header(..., description="Application ID sending the feedback"),
    x_soeid: str = Header(..., description="Consumer SOEID"),
    x_authorization_coin: str = Header(..., description="Authorization Coin ID"),
    content_type: str = Header(..., alias="Content-Type"),
    db: Session = Depends(get_db)
):
    """
    Upload JSON feedback.
    Table columns:
    - Application_Id
    - correlation_id
    - content
    - soeid
    - authorization_coin_id
    """
    # ---------------- Validate Content-Type ----------------
    if content_type.lower() != "application/json":
        logger.warning(f"[{x_correlation_id}] Invalid Content-Type: {content_type}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content-Type must be application/json"
        )

    if not x_authorization_coin:
        logger.warning(f"[{x_correlation_id}] Missing Authorization Coin ID")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=MISSING_AUTH_COIN_ID_ERROR
        )

    try:
        # ---------------- Read JSON body ----------------
        content_json = await request.json()
        logger.info(f"[{x_correlation_id}] JSON parsed successfully")

        # ---------------- Pydantic validation ----------------
        feedback_data = FeedbackCreate(
            Application_Id=x_application_id,
            correlation_id=x_correlation_id,
            content=content_json,
            soeid=x_soeid,
            authorization_coin_id=x_authorization_coin
        )
        logger.info(f"[{x_correlation_id}] Pydantic validation successful")

        # ---------------- Insert into DB ----------------
        db_feedback = models.Feedback(
            Application_Id=feedback_data.Application_Id,
            correlation_id=feedback_data.correlation_id,
            content=feedback_data.content,
            soeid=feedback_data.soeid,
            authorization_coin_id=feedback_data.authorization_coin_id
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        logger.info(f"[{x_correlation_id}] Feedback inserted successfully into DB")

        # ---------------- Response ----------------
        return {
            SUCCESS: True,
            MESSAGE: DATA_INSERTED,
            DETAILS: {
                "id": db_feedback.id,
                "table": models.TABLE_NAME,
                "Application_Id": db_feedback.Application_Id,
                "correlation_id": db_feedback.correlation_id
            }
        }

    except json.JSONDecodeError:
        logger.error(f"[{x_correlation_id}] Invalid JSON")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_JSON_MSG
        )
    except ValidationError as ve:
        logger.error(f"[{x_correlation_id}] Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        db.rollback()
        logger.error(f"[{x_correlation_id}] Database operation failed: {e}")
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


# models.py

from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

TABLE_NAME = "Feedback"

class Feedback(Base):
    """
    ORM model for the Feedback table.
    Columns:
    - id: Primary key
    - Application_Id: Application ID from header
    - correlation_id: Correlation ID from header
    - content: JSON feedback body
    - soeid: Consumer SOEID from header
    - authorization_coin_id: Authorization Coin ID from header
    - created_at: Timestamp of insertion
    """
    __tablename__ = TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    Application_Id = Column(String, nullable=False)
    correlation_id = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    soeid = Column(String, nullable=False)
    authorization_coin_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
