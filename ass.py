from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models import Feedback
from schemas import FeedbackResponse
from database import get_db, Base
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
    Fetch feedback records for a single day using full timestamp range.
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
