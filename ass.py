"""
===========================================================
📘 DATABASE CONNECTION MODULE
===========================================================
Description:
------------
This module initializes and manages the database connection
for the feedback analytics service.

It provides:
- SQLAlchemy Engine
- SessionLocal factory
- Declarative Base
- Dependency `get_db()` for FastAPI routes

It uses credentials loaded via YAML and environment configurations.

===========================================================
"""

from sqlalchemy.engine import make_url, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import yaml
from feedback.environment import BaseEnvironment
from exceptions.setup_log import setup_logger
from constant.constants import *

# ---------------------------------------------------------
# 🔹 Logger Setup
# ---------------------------------------------------------
try:
    logger = setup_logger()
except Exception:
    logger = None

# ---------------------------------------------------------
# 🔹 Base Declarative Class
# ---------------------------------------------------------
Base = declarative_base()

# ---------------------------------------------------------
# 🔹 Engine & Session Setup
# ---------------------------------------------------------
try:
    environment = BaseEnvironment()
    pgvector_env = environment.vector_store_env

    # Load credentials
    credentials = yaml.safe_load(pgvector_env.credentials_path.read_text())

    connect_args = {
        "options": f"-c search_path=extensions,{pgvector_env.schema_name}",
        "application_name": environment.application_name,
        "sslmode": "verify-full",
        "sslrootcert": pgvector_env.ssl_cert_file,
    }

    # Create SQLAlchemy Engine
    engine = create_engine(
        url=make_url(pgvector_env.url).set(
            username=credentials["user"],
            password=credentials["password"]
        ),
        pool_size=pgvector_env.pool_size,
        connect_args=connect_args
    )

    # ✅ Define SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    if logger:
        logger.info("✅ Database engine and SessionLocal created successfully.")

except Exception as e:
    if logger:
        logger.error(f"❌ Failed to initialize database engine: {e}", exc_info=True)
    raise e


# ---------------------------------------------------------
# 🔹 Dependency: get_db()
# ---------------------------------------------------------
def get_db():
    """
    Provides a new SQLAlchemy session for database operations.

    Yields:
        db (Session): Database session object

    Ensures session closure after request completes.
    """
    db = SessionLocal()
    try:
        if logger:
            logger.info("✅ DB session opened successfully through CyberArk.")
        yield db
    finally:
        db.close()
        if logger:
            logger.info("🛑 DB session closed.")

