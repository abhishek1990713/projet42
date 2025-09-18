from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USER = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACb"
DB_NAME = "gssp_common"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()



from sqlalchemy import Column, Integer, Text, JSON, TIMESTAMP, func
from db import Base

class Feedback(Base):
    __tablename__ = "Feedback"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Text, nullable=False)
    consumer_id = Column(Text, nullable=False)
    authorization_coin_id = Column(Text, nullable=False)
    feedback_json = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())



from pydantic import BaseModel
from typing import Dict, Any

class FeedbackCreate(BaseModel):
    application_id: str
    consumer_id: str
    feedback_json: Dict[str, Any]


APP_ID_KEY = "application_id"
CONSUMER_ID_KEY = "consumer_id"
SUCCESS_MSG = "Feedback saved successfully."
MISSING_FIELDS_MSG = "Missing required fields: application_id, consumer_id, or authorization_coin_id."
CONFIG_FILE = "config.ini"



from sqlalchemy.exc import SQLAlchemyError
from models import Feedback
from db import SessionLocal
from constants import SUCCESS_MSG, MISSING_FIELDS_MSG, APP_ID_KEY, CONSUMER_ID_KEY

def insert_json(data: dict, authorization_coin_id: str, logger=None) -> dict:
    """
    Insert JSON into PostgreSQL using ORM.
    """
    application_id = data.get(APP_ID_KEY)
    consumer_id = data.get(CONSUMER_ID_KEY)

    if not application_id or not consumer_id or not authorization_coin_id:
        if logger:
            logger.error(MISSING_FIELDS_MSG)
        return {"success": False, "message": MISSING_FIELDS_MSG, "details": None}

    session = SessionLocal()
    try:
        feedback = Feedback(
            application_id=application_id,
            consumer_id=consumer_id,
            authorization_coin_id=authorization_coin_id,
            feedback_json=data,
        )
        session.add(feedback)
        session.commit()
        session.refresh(feedback)

        if logger:
            logger.info("Data inserted successfully using ORM.")

        return {
            "success": True,
            "details": {
                "message": SUCCESS_MSG,
                "table": Feedback.__tablename__,
                "application_id": application_id,
                "consumer_id": consumer_id,
                "authorization_coin_id": authorization_coin_id,
            },
        }
    except SQLAlchemyError as e:
        session.rollback()
        if logger:
            logger.error(f"Database operation failed: {e}")
        return {"success": False, "message": "Database operation failed.", "error": str(e)}
    finally:
        session.close()
        if logger:
            logger.info("Database session closed.")


from fastapi import FastAPI, Header, HTTPException
from schemas import FeedbackCreate
from crud import insert_json
from setup_log import setup_logger
from db import Base, engine

# Create tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Feedback API")

logger = setup_logger()

@app.post("/feedback")
def create_feedback(
    feedback: FeedbackCreate,
    authorization_coin_id: str = Header(..., description="Authorization Coin ID")
):
    """
    API to insert feedback JSON into PostgreSQL.
    """
    data = feedback.dict()

    result = insert_json(data, authorization_coin_id, logger)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result)

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=4900, reload=True)
