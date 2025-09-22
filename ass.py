import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy_utils import database_exists, create_database
from exceptions.setup_log import setup_logger
from constant.constants import *

# Logger setup
try:
    logger = setup_logger()
except Exception:
    logger = None

# SQLAlchemy URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    if logger:
        logger.info(DATABASE_ENGINE_SUCCESS)
except Exception as e:
    if logger:
        logger.critical(DATABASE_ENGINE_FAILURE.format(e))
    raise

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarative class
Base = declarative_base()

# Set session role for new connections
@event.listens_for(Engine, "connect")
def set_role(dbapi_connection, connection_record):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute(SET_ROLE_QUERY.format(DB_SESSION_ROLE))
        cursor.close()
        if logger:
            logger.info(SESSION_ROLE_SET_SUCCESS.format(DB_SESSION_ROLE))
    except Exception as e:
        if logger:
            logger.error(SESSION_ROLE_SET_FAILURE.format(e))
        raise

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        if logger:
            logger.info(DB_SESSION_CREATED)
        yield db
    except Exception as e:
        if logger:
            logger.error(DB_SESSION_ERROR.format(e))
        raise
    finally:
        db.close()
        if logger:
            logger.info(DB_SESSION_CLOSED)


from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from db.database import Base
from constant.constants import *

TABLE_NAME = TABLE

class Feedback(Base):
    """
    SQLAlchemy model for storing feedback JSON payload.
    Columns: correlation_id, application_id, soeid, authorization_coin_id, feedback_json
    """
    __tablename__ = TABLE_NAME
    __table_args__ = {"schema": GSSP_SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String, index=True)
    application_id = Column(String, index=True)
    soeid = Column(String, index=True)
    authorization_coin_id = Column(String, index=True)
    feedback_json = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())



from fastapi import HTTPException, status
from pydantic import BaseModel, validator
from typing import Dict, Any
from exceptions.setup_log import setup_logger
from constant.constants import *

# Logger setup
try:
    logger = setup_logger()
except Exception:
    logger = None

class FeedbackCreate(BaseModel):
    """
    Schema for validating nested feedback JSON.
    """
    application_id: str
    feedback_json: Dict[str, Any]

    @validator("feedback_json", pre=True, always=True)
    def validate_required_keys(cls, v, values, **kwargs):
        try:
            if not isinstance(v, dict):
                if logger:
                    logger.error(INVALID_JSON_MSG)
                raise ValueError(INVALID_JSON_MSG)

            if "extractedData" not in v or "feedback" not in v:
                if logger:
                    logger.error(MISSING_FIELDS_MSG)
                raise ValueError(MISSING_FIELDS_MSG)

            if logger:
                logger.info(VALIDATION_SUCCESS_LOG)
            return v
        except ValueError as e:
            if logger:
                logger.error(VALIDATION_ERROR_LOG.format(e))
            raise
        except Exception as e:
            if logger:
                logger.error(f"Unexpected validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e))
            )

class FeedbackResponse(BaseModel):
    id: int
    correlation_id: str
    application_id: str
    soeid: str
    authorization_coin_id: str
    feedback_json: Dict[str, Any]
    created_at: Any

    class Config:
        orm_mode = True


from fastapi import FastAPI, Request, HTTPException, Depends, Header, status
from sqlalchemy.orm import Session
from db.database import get_db, engine, Base
from models.models import Feedback
from service import schemas
from exceptions.setup_log import setup_logger
from constant.constants import *
import uvicorn

# Logger setup
try:
    logger = setup_logger()
except Exception:
    logger = None

app = FastAPI()

# Create tables on startup
@app.on_event("startup")
def create_db_and_tables():
    try:
        Base.metadata.create_all(bind=engine)
        if logger:
            logger.info(DB_TABLES_CREATED)
    except Exception as e:
        if logger:
            logger.error(DB_INIT_FAILURE.format(e))
        raise RuntimeError(DB_INIT_FAILURE_RUNTIME) from e

@app.post("/upload_json", status_code=status.HTTP_201_CREATED)
async def upload_json(
    request: Request,
    db: Session = Depends(get_db),
    x_correlation_id: str = Header(...),
    x_application_id: str = Header(...),
    x_soeid: str = Header(...),
    x_authorization_coin: str = Header(...)
):
    try:
        data = await request.json()
        if logger:
            logger.info(FILE_PARSED_AS_JSON)
    except Exception as e:
        if logger:
            logger.error(f"Failed to parse JSON: {e}")
        raise HTTPException(status_code=400, detail=INVALID_JSON_MSG)

    # Validate JSON
    try:
        feedback_data = schemas.FeedbackCreate(
            application_id=x_application_id,
            feedback_json=data
        )
        if logger:
            logger.info(VALIDATION_SUCCESS_LOG)
    except Exception as e:
        if logger:
            logger.error(VALIDATION_ERROR_LOG.format(e))
        raise HTTPException(status_code=400, detail=VALIDATION_FAILED_MSG)

    # Insert into DB
    try:
        db_feedback = Feedback(
            correlation_id=x_correlation_id,
            application_id=feedback_data.application_id,
            soeid=x_soeid,
            authorization_coin_id=x_authorization_coin,
            feedback_json=data
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        if logger:
            logger.info(DB_INSERT_SUCCESS_LOG)

        return {
            SUCCESS: True,
            "message": DATA_INSERTED,
            "details": {
                "id": db_feedback.id,
                "correlation_id": db_feedback.correlation_id,
                "application_id": db_feedback.application_id,
                "soeid": db_feedback.soeid
            }
        }
    except Exception as e:
        db.rollback()
        if logger:
            logger.error(DB_OPERATION_FAILED_LOG.format(e))
        raise HTTPException(status_code=500, detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e)))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# create_feedback_table_psycopg2.py

import psycopg2
from psycopg2 import sql

# ---------------- PostgreSQL Credentials ----------------
DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USERNAME = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACЬ"
DB_NAME = "gssp_common"
DB_SESSION_ROLE = "citi_pg_app_owner"
SCHEMA_NAME = "gssp_common"
TABLE_NAME = "Feedback"

# ---------------- SQL Statements ----------------
CREATE_SCHEMA_SQL = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
    sql.Identifier(SCHEMA_NAME)
)

CREATE_TABLE_SQL = sql.SQL("""
CREATE TABLE IF NOT EXISTS {}.{} (
    id SERIAL PRIMARY KEY,
    correlation_id VARCHAR NOT NULL,
    application_id VARCHAR NOT NULL,
    soeid VARCHAR NOT NULL,
    authorization_coin_id VARCHAR NOT NULL,
    feedback_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
)
""").format(sql.Identifier(SCHEMA_NAME), sql.Identifier(TABLE_NAME))

# ---------------- Connect and Execute ----------------
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Set session role
    cursor.execute(f"SET ROLE {DB_SESSION_ROLE};")
    print(f"Session role set: {DB_SESSION_ROLE}")

    # Create schema
    cursor.execute(CREATE_SCHEMA_SQL)
    print(f"Schema ensured: {SCHEMA_NAME}")

    # Create table
    cursor.execute(CREATE_TABLE_SQL)
    print(f"Table created/ensured: {SCHEMA_NAME}.{TABLE_NAME}")

except Exception as e:
    print(f"Error creating table: {e}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
