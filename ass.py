
# main.py
from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
import json

from db import Base, engine, get_db
from models import Feedback
from schemas import FeedbackResponse
from constants import APP_ID_KEY, CONSUMER_ID_KEY, SUCCESS_MSG, MISSING_FIELDS_MSG
from setup_log import setup_logger

logger = setup_logger()

# Create tables automatically if not exist
Base.metadata.create_all(bind=engine)

# FastAPI instance
app = FastAPI(title="Feedback API")

@app.post("/feedback", response_model=FeedbackResponse)
def insert_feedback(
    data: dict,
    authorization_coin_id: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Insert feedback JSON into PostgreSQL.
    - application_id, consumer_id -> from JSON body
    - authorization_coin_id -> from request header
    """

    application_id = data.get(APP_ID_KEY)
    consumer_id = data.get(CONSUMER_ID_KEY)

    # Validate fields
    if not application_id or not consumer_id or not authorization_coin_id:
        logger.error(MISSING_FIELDS_MSG)
        raise HTTPException(status_code=400, detail=MISSING_FIELDS_MSG)

    try:
        # ORM insert
        feedback_entry = Feedback(
            application_id=application_id,
            consumer_id=consumer_id,
            authorization_coin_id=authorization_coin_id,
            feedback_json=json.loads(json.dumps(data))
        )
        db.add(feedback_entry)
        db.commit()
        db.refresh(feedback_entry)

        logger.info("Data inserted successfully.")

        return FeedbackResponse(
            success=True,
            message=SUCCESS_MSG,
            details={
                "table": Feedback.__tablename__,
                "application_id": application_id,
                "consumer_id": consumer_id,
                "authorization_coin_id": authorization_coin_id,
            },
        )

    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed.")



# schemas.py
from pydantic import BaseModel
from typing import Dict, Any

class FeedbackBase(BaseModel):
    application_id: str
    consumer_id: str
    feedback_json: Dict[str, Any]

class FeedbackCreate(FeedbackBase):
    authorization_coin_id: str

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    details: Dict[str, Any] | None = None

    class Config:
        orm_mode = True

# models.py
from sqlalchemy import Column, Integer, Text, JSON, TIMESTAMP, func
from db import Base

class Feedback(Base):
    """
    ORM model for Feedback table.
    Stores application_id, consumer_id, authorization_coin_id, and full feedback JSON.
    """
    __tablename__ = "Feedback"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Text, nullable=False)
    consumer_id = Column(Text, nullable=False)
    authorization_coin_id = Column(Text, nullable=False)
    feedback_json = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


db.py
# db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from setup_log import setup_logger

logger = setup_logger()

# Database config
DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USER = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACb"
DB_NAME = "gssp_common"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI routes.
    Yields a SQLAlchemy session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# constants.py

# Keys expected in the uploaded JSON
APP_ID_KEY = "application_id"
CONSUMER_ID_KEY = "consumer_id"

# Messages
SUCCESS_MSG = "Data inserted successfully."
MISSING_FIELDS_MSG = "Missing required fields."

# Config file path (if needed)
CONFIG_FILE = "config.ini"

project/
│── constants.py
│── setup_log.py
│── db.py
│── models.py
│── schemas.py
│── main.py
