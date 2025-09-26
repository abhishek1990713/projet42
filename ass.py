from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from . import models, schemas
from .database import engine, get_db

import uvicorn

app = FastAPI(title="Feedback API", version="1.0")

# ---------------- Create Tables ----------------
models.Base.metadata.create_all(bind=engine)


# ---------------- Endpoint ----------------
@app.get("/fetch_feedback", response_model=List[schemas.FeedbackResponse])
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
            db.query(models.Feedback)
            .filter(models.Feedback.application_id == application_id)
            .filter(models.Feedback.created_at.between(start_datetime, end_datetime))
            .order_by(models.Feedback.id.asc())
            .all()
        )

        if not results:
            raise HTTPException(status_code=404, detail="No records found for the given application_id and date")

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- Run Server ----------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
