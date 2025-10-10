from fastapi import FastAPI, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uvicorn

from db.database import get_db
from models.models import Feedback
from exceptions.setup_log import setup_logger

app = FastAPI(title="Feedback Report API")

# Logger setup
try:
    logger = setup_logger()
except Exception:
    logger = None


@app.post("/feedback_report", response_model=List[Dict[str, Any]])
def feedback_report(
    x_document_id: str = Header(..., description="Document ID"),
    db: Session = Depends(get_db)
):
    """
    Fetch all feedback for a given document_id from header and return:
        - total count for each field
        - thumbs_up count
        - thumbs_down count
        - percentage thumbs_up / total
        - overall status per field
    """

    try:
        # Fetch all feedback responses for the given document_id
        results = (
            db.query(Feedback.feedback_response)
            .filter(Feedback.document_id == x_document_id)
            .all()
        )

        if not results:
            if logger:
                logger.warning(f"No feedback records found for document_id={x_document_id}")
            raise HTTPException(status_code=404, detail="No feedback records found")

        # Count total occurrences & thumbs_up/thumbs_down for each field
        field_stats = {}

        for (feedback_json,) in results:
            field_feedback = feedback_json.get("field_feedback", {})
            if isinstance(field_feedback, dict):
                for field, details in field_feedback.items():
                    if not isinstance(details, dict):
                        continue
                    status = details.get("status", "").lower().strip()
                    if field not in field_stats:
                        field_stats[field] = {"total": 0, "thumbs_up": 0, "thumbs_down": 0}

                    field_stats[field]["total"] += 1
                    if status == "thumbs_up":
                        field_stats[field]["thumbs_up"] += 1
                    elif status == "thumbs_down":
                        field_stats[field]["thumbs_down"] += 1

        # Calculate percentage and overall status for each field
        aggregated_feedback = {}
        for field, counts in field_stats.items():
            total = counts["total"]
            thumbs_up = counts["thumbs_up"]
            thumbs_down = counts["thumbs_down"]
            percentage = round((thumbs_up / total) * 100, 2) if total else 0.0

            # Overall status
            overall_status = "thumbs_up" if thumbs_up >= thumbs_down else "thumbs_down"

            aggregated_feedback[field] = {
                "total_count": total,
                "positive_count": thumbs_up,
                "negative_count": thumbs_down,
                "percentage": percentage,
                "status": overall_status
            }

        # Return a single dictionary inside a list
        return [{"field_feedback": aggregated_feedback}]

    except HTTPException:
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error in feedback_report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run("docid:app", host="0.0.0.0", port=8092, reload=True)
