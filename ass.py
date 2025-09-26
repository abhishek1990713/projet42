from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------- Database Config ----------------
DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USERNAME = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACЬ"
DB_NAME = "gssp_common"

DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from sqlalchemy import Column, Integer, String, DateTime, JSON
from .database import Base

class Feedback(Base):
    __tablename__ = "idp_feedback"
    __table_args__ = {"schema": "gssp_common"}

    audit_id = Column(Integer, primary_key=True, index=True)
    consumer_coin = Column(String, nullable=True)
    app_id = Column(String, nullable=False)
    app_name = Column(String, nullable=True)
    usecase_config_id = Column(String, nullable=True)
    request = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    feedback_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    correlation_id = Column(String, nullable=False)


from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

class FeedbackResponse(BaseModel):
    audit_id: int
    consumer_coin: str | None
    app_id: str
    app_name: str | None
    usecase_config_id: str | None
    request: Dict[str, Any] | None
    response: Dict[str, Any] | None
    feedback_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime | None
    created_by: str | None
    updated_by: str | None
    correlation_id: str

    class Config:
        orm_mode = True

class FeedbackCreate(BaseModel):
    feedback_json: Dict[str, Any]
# Logging and message constants
VALIDATION_SUCCESS_LOG = "Payload validation success"
VALIDATION_ERROR_LOG = "Payload validation failed: {}"
DB_UPDATE_SUCCESS_LOG = "Feedback updated successfully for app_id={}, correlation_id={}"
DB_OPERATION_FAILED_LOG = "DB operation failed: {}"

SUCCESS = "success"
DATA_UPDATED = "Feedback updated successfully"
VALIDATION_FAILED_MSG = "Payload validation failed"
UNEXPECTED_VALIDATION_ERROR_MSG = "Unexpected error: {}"
from fastapi import FastAPI, HTTPException, Depends, Header, status, Body
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Feedback
from service import schemas
from exceptions.setup_log import setup_logger
from constant.constants import *
from datetime import datetime
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Logger setup
try:
    logger = setup_logger()
except Exception:
    logger = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_json", status_code=status.HTTP_200_OK)
async def upload_json(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    correlation_id: str = Header(...),
    app_id: str = Header(...),
):
    # Validate input
    try:
        feedback_data = schemas.FeedbackCreate(feedback_json=payload)
        if logger:
            logger.info(VALIDATION_SUCCESS_LOG)
    except Exception as e:
        if logger:
            logger.error(VALIDATION_ERROR_LOG.format(e))
        raise HTTPException(status_code=400, detail=VALIDATION_FAILED_MSG)

    # Update feedback_json in existing row
    try:
        db_feedback = db.query(Feedback).filter(
            Feedback.correlation_id == correlation_id,
            Feedback.app_id == app_id
        ).first()

        if not db_feedback:
            raise HTTPException(
                status_code=404,
                detail=f"No record found for correlation_id={correlation_id} and app_id={app_id}"
            )

        db_feedback.feedback_json = payload
        db_feedback.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_feedback)

        if logger:
            logger.info(DB_UPDATE_SUCCESS_LOG.format(app_id, correlation_id))

        return {
            SUCCESS: True,
            "message": DATA_UPDATED,
            "details": {
                "audit_id": db_feedback.audit_id,
                "app_id": db_feedback.app_id,
                "correlation_id": db_feedback.correlation_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        if logger:
            logger.error(DB_OPERATION_FAILED_LOG.format(e))
        raise HTTPException(status_code=500, detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e)))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8092, reload=True)
