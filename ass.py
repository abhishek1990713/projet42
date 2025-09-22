# main.py

from fastapi import FastAPI, Header, Depends, HTTPException
from fastapi import Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database

from models import models
from db.database import engine, get_db, DB_NAME
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


# ---------------- Pydantic Schema ----------------
class FeedbackRequest(BaseModel):
    content: dict  # JSON payload goes here


# ---------------- Startup Event ----------------
@app.on_event("startup")
def create_db_and_tables():
    """
    Startup event:
    - Creates the database if it doesn't exist.
    - Creates all tables under gssp_common schema.
    """
    try:
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info(f"Database created: {DB_NAME}")

        models.Base.metadata.create_all(bind=engine)
        logger.info(f"Tables created successfully under schema gssp_common")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise RuntimeError(f"Failed to initialize DB") from e


# ---------------- Upload JSON Endpoint ----------------
@app.post("/upload_json")
async def upload_json(
    request_data: FeedbackRequest,
    x_correlation_id: str = Header(..., description="Correlation ID"),
    x_application_id: str = Header(..., description="Application ID"),
    x_soeid: str = Header(..., description="Consumer SOEID"),
    x_authorization_coin: str = Header(..., description="Authorization Coin ID"),
    db: Session = Depends(get_db)
):
    """
    Store the JSON in 'content' column and headers in other columns.
    """
    try:
        # Get content from request body
        payload = request_data.content
        logger.info(f"[{x_correlation_id}] JSON received in content field")

        # Insert into database
        db_feedback = models.Feedback(
            Application_Id=x_application_id,
            correlation_id=x_correlation_id,
            content=payload,
            soeid=x_soeid,
            authorization_coin_id=x_authorization_coin
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        logger.info(f"[{x_correlation_id}] Feedback stored in DB with ID {db_feedback.id}")

        return {
            "success": True,
            "id": db_feedback.id,
            "Application_Id": db_feedback.Application_Id,
            "correlation_id": db_feedback.correlation_id
        }

    except Exception as e:
        db.rollback()
        logger.error(f"[{x_correlation_id}] DB operation failed: {e}")
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")


# ---------------- Main Entry Point ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
