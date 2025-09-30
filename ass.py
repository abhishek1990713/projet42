from datetime import datetime
from typing import List
from fastapi import FastAPI, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Feedback
from schemas import FeedbackResponse

app = FastAPI()


@app.get("/feedback")
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    start_day: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_day: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Fetch feedback records for a given application_id 
    within a specific date range (start_day to end_day).
    """

    try:
        # Validate date formats
        try:
            datetime.strptime(start_day, "%Y-%m-%d")
            datetime.strptime(end_day, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Expand into full timestamp range
        start_datetime = f"{start_day} 00:00:00"
        end_datetime = f"{end_day} 23:59:59"

        # Query feedback records
        feedbacks = db.query(Feedback).filter(
            Feedback.application_id == application_id,
            Feedback.created_at.between(start_datetime, end_datetime)
        ).order_by(Feedback.id.asc()).all()

        if not feedbacks:
            raise HTTPException(
                status_code=404,
                detail="No feedback records found for given filters"
            )

        # Convert ORM objects → Pydantic Response
        feedback_list = [FeedbackResponse.from_orm(fb) for fb in feedbacks]

        # ✅ Proper structured success response
        return {
            "status": "success",
            "message": f"Fetched {len(feedback_list)} feedback records successfully",
            "data": feedback_list
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching feedback: {str(e)}"
        )
