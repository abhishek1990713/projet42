from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models import Feedback
from logger_config import logger


def feedback_report(application_id: str, start_date: str, end_date: str, db: Session):
    """
    Function to generate aggregated feedback statistics for a given application_id
    and date range (start_date to end_date).

    Args:
        application_id (str): Application ID to filter feedbacks.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        db (Session): SQLAlchemy database session.

    Returns:
        list: A list containing one dictionary with aggregated feedback summary.
    """
    try:
        logger.info(f"Fetching feedback report for application_id={application_id}, "
                    f"Date Range: {start_date} to {end_date}")

        # -------------------------------------------------------------
        # Fetch all feedback entries matching filters
        # -------------------------------------------------------------
        results = (
            db.query(Feedback.feedback_response)
            .filter(
                and_(
                    Feedback.application_id == application_id,
                    Feedback.created_on >= start_date,
                    Feedback.created_on <= end_date,
                )
            )
            .all()
        )

        if not results:
            logger.warning(f"No feedback records found for application_id={application_id}")
            return [{"message": "No feedback records found for the given criteria"}]

        # -------------------------------------------------------------
        # Count thumbs_up/thumbs_down per field
        # -------------------------------------------------------------
        field_stats = {}

        for (feedback_json,) in results:
            # Extract nested feedback JSON structure
            field_feedback = feedback_json.get("feedback", {}).get("field_feedback", {})

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
                        "thumbs_down_count": 0,
                    }

                field_stats[field]["feedback_count"] += 1

                if status == "thumbs_up":
                    field_stats[field]["thumbs_up_count"] += 1
                elif status == "thumbs_down":
                    field_stats[field]["thumbs_down_count"] += 1

        # -------------------------------------------------------------
        # Aggregate percentages and final feedback summary
        # -------------------------------------------------------------
        aggregated_feedback = {}

        for field, counts in field_stats.items():
            feedback_count = counts["feedback_count"]
            thumbs_up_count = counts["thumbs_up_count"]
            thumbs_down_count = counts["thumbs_down_count"]

            percentage = round((thumbs_up_count / feedback_count) * 100, 2) if feedback_count else 0.0
            overall_status = "thumbs_up" if thumbs_up_count >= thumbs_down_count else "thumbs_down"

            aggregated_feedback[field] = {
                "status": overall_status,
                "percentage": percentage,
                "feedback_count": feedback_count,
                "thumbs_up_count": thumbs_up_count,
                "thumbs_down_count": thumbs_down_count,
            }

        # -------------------------------------------------------------
        # Return final summarized result
        # -------------------------------------------------------------
        return [
            {
                "application_id": application_id,
                "start_date": start_date,
                "end_date": end_date,
                "field_feedback": aggregated_feedback,
            }
        ]

    except Exception as e:
        logger.error(f"Error in feedback_report: {str(e)}", exc_info=True)
        return [{"error": f"Failed to generate feedback report: {str(e)}"}]
