from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from db.models import FeedbackResponse   # ORM model class
from logger_config import logger


def get_all_document_types(db: Session):
    """
    Fetch all distinct document types available in the feedback table.
    Returns a list like:
      ["passport", "license", "residence_certificate"]
    """
    try:
        logger.info("Fetching all distinct document types...")
        results = db.query(FeedbackResponse.document_type).distinct().all()
        return [row.document_type for row in results if row.document_type]
    except Exception as e:
        logger.error(f"Error fetching document types: {str(e)}", exc_info=True)
        return []


def get_document_percentage_stats(db: Session, application_id: str = None,
                                  start_date: str = None, end_date: str = None):
    """
    Calculate document feedback percentage distribution per application.

    Parameters
    ----------
    db : Session
        Active SQLAlchemy database session.
    application_id : str, optional
        Specific application_id to filter records (default is None — fetch all).
    start_date : str, optional
        Start date for filtering records based on 'created_at' (format: 'YYYY-MM-DD').
    end_date : str, optional
        End date for filtering records based on 'created_at' (format: 'YYYY-MM-DD').

    Returns
    -------
    list[dict]
        A list of dictionaries, where each dictionary contains:
        {
            "application_id": "APP123",
            "total_documents": 100,
            "greater_than_81": 40,
            "range_71_to_80": 30,
            "range_50_to_70": 20,
            "less_than_50": 10,
            "summary_percentage": {
                ">81%": 40.0,
                "71–80%": 30.0,
                "50–70%": 20.0,
                "<50%": 10.0
            }
        }
    """
    try:
        logger.info("Fetching document percentage statistics...")

        # Base query
        query = db.query(
            FeedbackResponse.application_id,
            func.count(FeedbackResponse.id).label("total_docs"),
            func.sum(case((FeedbackResponse.percentage > 81, 1), else_=0)).label("above_81"),
            func.sum(case(
                ((FeedbackResponse.percentage >= 71) & (FeedbackResponse.percentage <= 80), 1),
                else_=0
            )).label("range_71_80"),
            func.sum(case(
                ((FeedbackResponse.percentage >= 50) & (FeedbackResponse.percentage <= 70), 1),
                else_=0
            )).label("range_50_70"),
            func.sum(case((FeedbackResponse.percentage < 50, 1), else_=0)).label("below_50")
        )

        # Apply filters
        filters = []
        if application_id:
            filters.append(FeedbackResponse.application_id == application_id)
            logger.info(f"Filtering by application_id: {application_id}")

        if start_date and end_date:
            filters.append(and_(FeedbackResponse.created_at >= start_date,
                                FeedbackResponse.created_at <= end_date))
            logger.info(f"Filtering by date range: {start_date} to {end_date}")
        elif start_date:
            filters.append(FeedbackResponse.created_at >= start_date)
            logger.info(f"Filtering from start_date: {start_date}")
        elif end_date:
            filters.append(FeedbackResponse.created_at <= end_date)
            logger.info(f"Filtering until end_date: {end_date}")

        if filters:
            query = query.filter(and_(*filters))

        query = query.group_by(FeedbackResponse.application_id)
        results = query.all()

        if not results:
            logger.warning("No records found for given filters or dataset is empty")
            return []

        response_data = []
        for row in results:
            total_docs = row.total_docs or 0
            data = {
                "application_id": row.application_id,
                "total_documents": total_docs,
                "greater_than_81": row.above_81 or 0,
                "range_71_to_80": row.range_71_80 or 0,
                "range_50_to_70": row.range_50_70 or 0,
                "less_than_50": row.below_50 or 0,
                "summary_percentage": {
                    ">81%": round((row.above_81 / total_docs) * 100, 2) if total_docs else 0,
                    "71–80%": round((row.range_71_80 / total_docs) * 100, 2) if total_docs else 0,
                    "50–70%": round((row.range_50_70 / total_docs) * 100, 2) if total_docs else 0,
                    "<50%": round((row.below_50 / total_docs) * 100, 2) if total_docs else 0,
                },
            }
            response_data.append(data)

        logger.info("Document percentage statistics computed successfully.")
        return response_data

    except Exception as e:
        logger.error(f"Error in get_document_percentage_stats: {str(e)}", exc_info=True)
        return []
