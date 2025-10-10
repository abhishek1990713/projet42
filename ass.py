from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models import Feedback
from app.logger_config import logger

router = APIRouter()

@router.post("/feedback_report", response_model=List[Dict[str, Any]])
def feedback_report(
    application_id: str = Query(..., description="Application ID"),
    db: Session = Depends(get_db),
):
    """
    Fetch feedback data for the given application_id and calculate 
    percentage = (thumbs_up_count / total_field_count) * 100 
    for each unique field across all records.
    """
    try:
        # Fetch all feedbacks for given application_id
        results = (
            db.query(
                Feedback.file_id,
                Feedback.document_id,
                Feedback.feedback_response
            )
            .filter(Feedback.application_id == application_id)
            .order_by(Feedback.id.asc())
            .all()
        )

        if not results:
            if logger:
                logger.warning(f"No feedback records found for application_id={application_id}")
            raise HTTPException(
                status_code=404,
                detail="No feedback records found for the given application_id",
            )

        # Step 1: Count total occurrences & thumbs_up occurrences for each field
        field_counts = {}
        for _, _, feedback_json in results:
            field_feedback = feedback_json.get("field_feedback", {})
            for field, details in field_feedback.items():
                status = details.get("status", "").lower()
                if field not in field_counts:
                    field_counts[field] = {"total": 0, "thumbs_up": 0}
                field_counts[field]["total"] += 1
                if status == "thumbs_up":
                    field_counts[field]["thumbs_up"] += 1

        # Step 2: Compute percentage for each field
        field_percentages = {
            field: round((counts["thumbs_up"] / counts["total"]) * 100, 2)
            for field, counts in field_counts.items() if counts["total"] > 0
        }

        # Step 3: Build the response
        response_data = []
        for file_id, document_id, feedback_json in results:
            field_feedback = feedback_json.get("field_feedback", {})
            enriched_feedback = {}
            for field, details in field_feedback.items():
                enriched_feedback[field] = {
                    **details,
                    "percentage": field_percentages.get(field, 0)
                }

            response_data.append({
                "file_id": file_id,
                "document_id": document_id,
                "field_feedback": enriched_feedback
            })

        if logger:
            logger.info(f"Fetched {len(results)} feedback records for application_id={application_id}")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error fetching feedback_response: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
