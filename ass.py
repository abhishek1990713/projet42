from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from db.database import get_db
from models.models import Feedback
from exceptions.setup_log import setup_logger

logger = setup_logger()
router = APIRouter()

@router.post("/feedback_report", response_model=List[Dict[str, Any]])
def feedback_report(
    application_id: str = Query(..., description="Application ID"),
    db: Session = Depends(get_db),
):
    """
    Generate a single aggregated field_feedback dictionary with thumbs_up percentage
    for all fields across all records.
    percentage = (thumbs_up / total_occurrences) * 100
    """
    try:
        # Fetch all feedbacks for the given application_id
        results = (
            db.query(Feedback.feedback_response)
            .filter(Feedback.application_id == application_id)
            .all()
        )

        if not results:
            if logger:
                logger.warning(f"No feedback records found for application_id={application_id}")
            raise HTTPException(status_code=404, detail="No feedback records found")

        # Count total occurrences & thumbs_up for each field
        field_stats = {}
        for (feedback_json,) in results:
            field_feedback = feedback_json.get("field_feedback", {})
            if isinstance(field_feedback, dict):
                for field, details in field_feedback.items():
                    if not isinstance(details, dict):
                        continue
                    status = details.get("status", "").lower().strip()
                    if field not in field_stats:
                        field_stats[field] = {"total": 0, "thumbs_up": 0}
                    field_stats[field]["total"] += 1
                    if status == "thumbs_up":
                        field_stats[field]["thumbs_up"] += 1

        # Calculate percentage for each field
        aggregated_feedback = {}
        for field, counts in field_stats.items():
            total = counts["total"]
            thumbs_up = counts["thumbs_up"]
            percentage = round((thumbs_up / total) * 100, 2) if total > 0 else 0.0
            # Use last status encountered for that field (optional)
            aggregated_feedback[field] = {
                "status": "thumbs_up" if thumbs_up >= (total - thumbs_up) else "thumbs_down",
                "percentage": percentage
            }

        # Return a single dictionary inside a list
        return [{"field_feedback": aggregated_feedback}]

    except HTTPException:
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error in feedback_report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
