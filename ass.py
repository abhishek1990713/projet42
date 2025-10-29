from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.models import Feedback
from exceptions.setup_log import setup_logger
from db.database import SessionLocal
from constant.constants import *
from datetime import datetime

# ---------------------------------------------------------------------
# Logger setup
# ---------------------------------------------------------------------
try:
    logger = setup_logger()
except Exception:
    logger = None


# ---------------------------------------------------------------------
# Function: get_feedback_responses_by_app
# ---------------------------------------------------------------------
def get_feedback_responses_by_app(application_id: str, start_date: str, end_date: str):
    """
    Fetch all feedback_response JSON objects for a specific application_id
    within a given start and end date range.
    """

    db: Session = SessionLocal()

    try:
        if logger:
            logger.info(
                f"Fetching full feedback_response data for application_id={application_id}, "
                f"start_date={start_date}, end_date={end_date}"
            )

        # Convert string dates into full datetime range
        start_datetime = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S")

        if logger:
            logger.info(f"Adjusted datetime range: start={start_datetime}, end={end_datetime}")

        # Query all feedback responses for the given application ID and date range
        feedback_records = (
            db.query(
                Feedback.feedback_id,
                Feedback.application_id,
                Feedback.document_id,
                Feedback.file_name,
                Feedback.feedback_response,
                Feedback.created_on
            )
            .filter(
                and_(
                    Feedback.application_id == application_id,
                    Feedback.created_on >= start_datetime,
                    Feedback.created_on <= end_datetime
                )
            )
            .all()
        )

        # Build response list
        result = []
        for record in feedback_records:
            result.append({
                "feedback_id": record.feedback_id,
                "application_id": record.application_id,
                "document_id": record.document_id,
                "file_name": record.file_name,
                "feedback_response": record.feedback_response,
                "created_on": record.created_on.strftime("%Y-%m-%d %H:%M:%S") if record.created_on else None
            })

        if logger:
            logger.info(FEEDBACK_RESPONSE_FETCH_SUCCESS.format(application_id, len(result)))

        return {
            "applicationId": application_id,
            "startDate": start_date,
            "endDate": end_date,
            "totalRecords": len(result),
            "feedbackResponses": result
        }

    except Exception as e:
        if logger:
            logger.error(FEEDBACK_RESPONSE_FETCH_FAILURE.format(str(e)))
        return {"error": str(e)}

    finally:
        db.close()
        if logger:
            logger.info(DB_SESSION_CLOSED)
