from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
import logging
from models import Feedback  # adjust import path if needed

logger = logging.getLogger(__name__)

def feedback_report(application_id: str, start_date: str, end_date: str, db: Session):
    """
    Generate feedback report for given application_id and date range.
    Calculates thumbs-up/thumbs-down statistics for each field.
    """
    try:
        # Convert string dates to datetime
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Fetch feedback within date range
        results = (
            db.query(Feedback.feedback_response)
            .filter(Feedback.application_id == application_id)
            .filter(Feedback.created_at.between(start_dt, end_dt))
            .all()
        )

        if not results:
            logger.warning(f"No feedback records found for application_id={application_id}")
            raise HTTPException(status_code=404, detail="No feedback records found")

        # Initialize stats
        field_stats = {}

        # Loop through feedback responses
        for (feedback_json,) in results:
            field_feedback = feedback_json.get("field_feedback", {})
            if not isinstance(field_feedback, dict):
                continue

            for field, details in field_feedback.items():
                if not isinstance(details, dict):
                    continue

                status = details.get("status", "").lower().strip()
                if field not in field_stats:
                    field_stats[field] = {
                        "feedback_count": 0,
                        "thumbs_up_count": 0,
                        "thumbs_down_count": 0
                    }

                field_stats[field]["feedback_count"] += 1
                if status == "thumbs_up":
                    field_stats[field]["thumbs_up_count"] += 1
                elif status == "thumbs_down":
                    field_stats[field]["thumbs_down_count"] += 1

        # Aggregate feedback data
        aggregated_feedback = {}
        for field, counts in field_stats.items():
            feedback_count = counts["feedback_count"]
            thumbs_up_count = counts["thumbs_up_count"]
            thumbs_down_count = counts["thumbs_down_count"]

            percentage = round((thumbs_up_count / feedback_count) * 100, 2) if feedback_count > 0 else 0.0
            overall_status = "thumbs_up" if thumbs_up_count >= thumbs_down_count else "thumbs_down"

            aggregated_feedback[field] = {
                "status": overall_status,
                "percentage": percentage,
                "feedback_count": feedback_count,
                "thumbs_up_count": thumbs_up_count,
                "thumbs_down_count": thumbs_down_count,
            }

        # Return structured response
        return [{
            "application_id": application_id,
            "start_date": start_date,
            "end_date": end_date,
            "field_feedback": aggregated_feedback
        }]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating feedback report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
