import logging
from fastapi import FastAPI, HTTPException, Depends, Header, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy_utils import database_exists, create_database
import uvicorn

from . import models, schemas
from .database import engine, get_db, DB_NAME
from .setup_log import setup_logger
from .constants import *

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception:
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

# ---------------- FastAPI App ----------------
app = FastAPI(title="Feedback API")

# ---------------- Startup Event ----------------
@app.on_event("startup")
def create_db_and_tables():
    """
    Create the database, schema, and tables at application startup if they do not exist.
    """
    try:
        # ---------------- Create DB if missing ----------------
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info(DB_CREATED.format(DB_NAME))

        # ---------------- Create schema if missing ----------------
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS gssp_common;"))
            conn.commit()

        # ---------------- Create tables ----------------
        models.Base.metadata.create_all(bind=engine)
        logger.info(DB_TABLES_CREATED)

    except Exception as e:
        logger.error(DB_INIT_FAILURE.format(e))
        raise RuntimeError(DB_INIT_FAILURE_RUNTIME) from e


# ---------------- Upload Feedback Endpoint ----------------
@app.post(UPLOAD_JSON, response_model=schemas.FeedbackResponse, status_code=status.HTTP_201_CREATED)
def upload_json(
    payload: dict,
    db: Session = Depends(get_db),
    x_correlation_id: str = Header(..., alias="x-correlation-id"),
    x_application_id: str = Header(..., alias="x-application-id"),
    x_soeid: str = Header(..., alias="x-soeid"),
    x_authorization_coin: str = Header(..., alias="X-Authorization-Coin")
):
    """
    Endpoint to save JSON feedback data along with headers.
    The full request body is stored in feedback_json.
    """
    try:
        if not payload:
            logger.warning(INVALID_JSON_LOG)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID_JSON_MSG,
            )

        # ---------------- Insert into DB ----------------
        db_feedback = models.Feedback(
            correlation_id=x_correlation_id,
            application_id=x_application_id,
            soeid=x_soeid,
            authorization_coin=x_authorization_coin,
            feedback_json=payload,
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        logger.info(DB_INSERT_SUCCESS_LOG)

        return db_feedback

    except HTTPException as http_exc:
        logger.error(HTTP_EXCEPTION_LOG.format(http_exc.detail))
        raise http_exc
    except Exception as e:
        db.rollback()
        logger.error(DB_OPERATION_FAILED_LOG.format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR_MSG.format(str(e)),
        )


# ---------------- Main Entry Point ----------------
if __name__ == "__main__":
    uvicorn.run(
        UVICORN_APP,
        host=UVICORN_HOST,
        port=UVICORN_PORT,
        log_level=UVICORN_LOG_LEVEL,
        reload=UVICORN_RELOAD,
    )

import os
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from .setup_log import setup_logger
from .constants import (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_SESSION_ROLE,
    DATABASE_ENGINE_SUCCESS,
    DATABASE_ENGINE_FAILURE,
    DB_SESSION_CREATED,
    DB_SESSION_CLOSED,
    DB_SESSION_ERROR,
    SET_ROLE_QUERY,
    SESSION_ROLE_SET_SUCCESS,
    SESSION_ROLE_SET_FAILURE,
)

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception:
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

# ---------------- Database URL ----------------
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ---------------- Engine Creation ----------------
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, future=True)
    logger.info(DATABASE_ENGINE_SUCCESS)
except Exception as e:
    logger.critical(DATABASE_ENGINE_FAILURE.format(e))
    raise

# ---------------- Session Factory ----------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# ---------------- Base Class ----------------
Base = declarative_base()

# ---------------- Role Setter ----------------
@event.listens_for(Engine, "connect")
def set_role(dbapi_connection, connection_record):
    """
    Event listener to set the DB session role for each new connection.
    """
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute(SET_ROLE_QUERY.format(DB_SESSION_ROLE))
        cursor.close()
        logger.info(SESSION_ROLE_SET_SUCCESS.format(DB_SESSION_ROLE))
    except Exception as e:
        logger.error(SESSION_ROLE_SET_FAILURE.format(e))
        raise

# ---------------- Dependency ----------------
def get_db():
    """
    Dependency to provide a database session for FastAPI endpoints.

    Yields:
        Session: A SQLAlchemy session instance.

    Ensures that the session is closed after use.
    """
    db = SessionLocal()
    try:
        logger.info(DB_SESSION_CREATED)
        yield db
    except Exception as e:
        logger.error(DB_SESSION_ERROR.format(e))
        raise
    finally:
        db.close()
        logger.info(DB_SESSION_CLOSED)

