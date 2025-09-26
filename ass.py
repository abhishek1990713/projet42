"""
=========================================================
 database.py - Database Connection and Session Handling
=========================================================

Purpose:
--------
This module is responsible for handling the database connection 
using SQLAlchemy ORM. It integrates with CyberArk (via BaseEnvironment) 
to securely fetch credentials and establish a connection to PostgreSQL.

Key Responsibilities:
---------------------
1. Configure the SQLAlchemy database engine with:
   - CyberArk-managed credentials
   - SSL options
   - Schema search_path
   - Application name for tracking
2. Provide a declarative Base class (`Base`) for ORM models.
3. Expose a dependency (`get_db`) for FastAPI routes that:
   - Opens a new DB session.
   - Yields it to the route handler.
   - Ensures proper cleanup (close session).
4. Log connection setup through centralized logger.

Why This Matters:
-----------------
By centralizing DB setup in this file, other parts of the application 
(models, endpoints, etc.) can reuse a single reliable connection setup. 
This makes the system more secure, maintainable, and consistent.
"""




"""
=========================================================
 models.py - SQLAlchemy ORM Models
=========================================================

Purpose:
--------
Defines the database tables as Python classes using SQLAlchemy ORM.  
Each class maps to a database table and its columns, making it possible 
to query the database in an object-oriented way instead of raw SQL.

Key Responsibilities:
---------------------
1. Define ORM models that represent tables in PostgreSQL.
2. Specify columns, datatypes, constraints, and schema.
3. Provide a reusable Base class (imported from database.py).

Why This Matters:
-----------------
ORM models act as the foundation for database operations. Instead of 
writing raw SQL queries, we can now use ORM objects like `Feedback` 
to perform queries, inserts, and updates with Pythonic syntax.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from database import Base

class Feedback(Base):
    """
    ORM model for the 'idp_feedback' table inside the 'gssp_common' schema.
    
    Represents user feedback records including:
    - Application ID
    - Correlation ID
    - User (SOEID)
    - Authorization Coin ID
    - Feedback JSON payload
    - Timestamp of record creation
    """
    __tablename__ = "idp_feedback"
    __table_args__ = {"schema": "gssp_common"}  # specify schema

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String, nullable=False)
    correlation_id = Column(String, nullable=False)
    soeid = Column(String, nullable=False)
    authorization_coin_id = Column(String, nullable=False)
    feedback_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=Fals
"""
=========================================================
 schemas.py - Pydantic Models for Validation
=========================================================

Purpose:
--------
Defines request and response models using Pydantic. These models ensure:
1. Validation of incoming data (type-checking).
2. Serialization of ORM objects into JSON responses.
3. Clear contracts between API routes and clients.

Key Responsibilities:
---------------------
1. Define `FeedbackResponse` for API responses.
2. Enable `.from_orm()` to convert SQLAlchemy ORM objects to JSON.
3. Provide a clear schema for documentation (via FastAPI Swagger UI).

Why This Matters:
-----------------
Schemas guarantee data integrity between the database and API responses.  
They enforce type-safety and prevent accidental leakage of unwanted fields.
"""

from pydantic import BaseModel
from typing import Dict
from datetime import datetime

class FeedbackResponse(BaseModel):
    """
    Response schema for feedback records fetched from the database.
    """
    id: int
    application_id: str
    correlation_id: str
    soeid: str
    authorization_coin_id: str
    feedback_json: Dict
    created_at: datetime

    class Config:
        orm_mode = True  # allows returning SQLAlchemy objects directly
"""
=========================================================
 main.py - FastAPI Application Entry Point
=========================================================

Purpose:
--------
This file defines the FastAPI application and its routes. It serves 
as the main entry point for running the service.

Key Responsibilities:
---------------------
1. Initialize the FastAPI app with metadata (title, version).
2. Setup logging for error handling.
3. Define API endpoints, including:
   - `/fetch_feedback`: Retrieve feedback records by application_id and date.
4. Handle database sessions via dependency injection (`get_db`).
5. Return validated responses using Pydantic schemas.

Why This Matters:
-----------------
`main.py` ties everything together:
- `database.py` provides DB sessions.
- `models.py` defines ORM table mappings.
- `schemas.py` validates responses.
- `main.py` exposes routes to the outside world.

Example Usage:
--------------
GET /fetch_feedback?application_id=157013&day=2025-09-25

Response (200 OK):
[
  {
    "id": 1,
    "application_id": "157013",
    "correlation_id": "abcd-1234",
    "soeid": "user1",
    "authorization_coin_id": "auth123",
    "feedback_json": { "rating": 5, "comment": "Good" },
    "created_at": "2025-09-25T08:45:00"
  }
]
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models import Feedback
from schemas import FeedbackResponse
from database import get_db
from exceptions.setup_log import setup_logger

import uvicorn

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception:
    logger = None

# ---------------- FastAPI App ----------------
app = FastAPI(title="Feedback API", version="1.0")


# ---------------- Endpoint ----------------
@app.get("/fetch_feedback", response_model=List[FeedbackResponse])
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    day: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Fetch feedback records for a given application_id and date.
    Uses SQLAlchemy ORM and returns validated JSON responses.
    """
    try:
        # Validate date format
        try:
            datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        start_datetime = f"{day} 00:00:00"
        end_datetime = f"{day} 23:59:59"

        results = (
            db.query(Feedback)
            .filter(Feedback.application_id == application_id)
            .filter(Feedback.created_at.between(start_datetime, end_datetime))
            .order_by(Feedback.id.asc())
            .all()
        )

        if not results:
            raise HTTPException(status_code=404, detail="No records found for the given application_id and date")

        return results

    except Exception as e:
        if logger:
            logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- Run Server ----------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
