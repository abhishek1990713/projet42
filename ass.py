from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from .database import Base

class Feedback(Base):
    """
    Feedback table model.
    Stores request headers as separate columns and the full request body in feedback_json.
    """

    __tablename__ = "feedback"   # Table name in DB

    id = Column(Integer, primary_key=True, index=True)  # Auto-increment primary key
    correlation_id = Column(String, nullable=False, index=True)  # From header: x-correlation-id
    application_id = Column(String, nullable=False, index=True)  # From header: x-application-id
    soeid = Column(String, nullable=False, index=True)  # From header: x-soeid
    authorization_coin = Column(String, nullable=False)  # From header: X-Authorization-Coin
    feedback_json = Column(JSON, nullable=False)  # Full request body (extractedData + feedback)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Auto timestamp


import os
import logging
from sqlalchemy import create_engine, event
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
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    logger.info(DATABASE_ENGINE_SUCCESS)
except Exception as e:
    logger.critical(DATABASE_ENGINE_FAILURE.format(e))
    raise

# ---------------- Session Factory ----------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
