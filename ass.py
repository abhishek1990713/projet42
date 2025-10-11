from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from db.database import SessionLocal
from db.models import Feedback
from logger_config import logger


def get_document_percentage_stats(application_id: str, start_date: str, end_date: str):
    """
    Calculates feedback percentage stats filtered by application_id and date range.

    Args:
        application_id (str): Application identifier.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).

    Returns:
        list: Summary dictionary containing percentage statistics.
    """
    try:
        db: Session = SessionLocal()
        logger.info(
            f"Fetching document percentage statistics for application_id={application_id}, "
            f"start_date={start_date}, end_date={end_date}"
        )

        # Common filter condition
        filter_condition = and_(
            Feedback.application_id == application_id,
            Feedback.created_on >= start_date,
            Feedback.created_on <= end_date
        )

        # Stats calculation
        total_docs = db.query(func.count(Feedback.id)).filter(filter_condition).scalar()
        above_81 = db.query(func.count()).filter(filter_condition, Feedback.percentage > 81).scalar()
        range_71_80 = db.query(func.count()).filter(
            filter_condition,
            Feedback.percentage >= 71,
            Feedback.percentage <= 80
        ).scalar()
        range_50_70 = db.query(func.count()).filter(
            filter_condition,
            Feedback.percentage >= 50,
            Feedback.percentage <= 70
        ).scalar()
        below_50 = db.query(func.count()).filter(filter_condition, Feedback.percentage < 50).scalar()

        logger.info(
            f"Stats for {application_id}: total={total_docs}, >81={above_81}, "
            f"71–80={range_71_80}, 50–70={range_50_70}, <50={below_50}"
        )

        result = [
            {
                "application_id": application_id,
                "start_date": start_date,
                "end_date": end_date,
                "total_documents": total_docs,
                "greater_than_81": above_81,
                "range_71_to_80": range_71_80,
                "range_50_to_70": range_50_70,
                "less_than_50": below_50,
                "summary_percentage": {
                    ">81%": round((above_81 / total_docs) * 100, 2) if total_docs else 0,
                    "71–80%": round((range_71_80 / total_docs) * 100, 2) if total_docs else 0,
                    "50–70%": round((range_50_70 / total_docs) * 100, 2) if total_docs else 0,
                    "<50%": round((below_50 / total_docs) * 100, 2) if total_docs else 0,
                },
            }
        ]

        return result

    except Exception as e:
        logger.error(f"Error in get_document_percentage_stats: {str(e)}")
        return {"error": str(e)}

    finally:
        db.close()
from fastapi import FastAPI, Header, HTTPException
from document_stats import get_document_percentage_stats
from logger_config import logger

app = FastAPI(title="Feedback Stats API")


@app.get("/feedback/stats", tags=["Feedback Stats"])
def fetch_feedback_stats(
    application_id: str = Header(None),
    start_date: str = Header(None),
    end_date: str = Header(None)
):
    """
    GET endpoint to fetch feedback percentage statistics by application_id and date range.

    Headers:
        - application_id: (str) Application ID to filter results.
        - start_date: (str, format YYYY-MM-DD)
        - end_date: (str, format YYYY-MM-DD)

    Example:
        application_id: APP001
        start_date: 2025-09-01
        end_date: 2025-09-30
    """
    try:
        if not application_id or not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail="Headers 'application_id', 'start_date', and 'end_date' are required."
            )

        logger.info(
            f"Received request for application_id={application_id}, start_date={start_date}, end_date={end_date}"
        )
        result = get_document_percentage_stats(application_id, start_date, end_date)

        if not result or (isinstance(result, dict) and "error" in result):
            raise HTTPException(
                status_code=404,
                detail=f"No records found for application_id={application_id} within given date range."
            )

        return result

    except HTTPException as http_err:
        logger.warning(f"HTTP error: {http_err.detail}")
        raise http_err

    except Exception as e:
        logger.error(f"Unexpected error in fetch_feedback_stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
