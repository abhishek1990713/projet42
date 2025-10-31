from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from models.models import Feedback
from db.database import SessionLocal
from exceptions.setup_log import setup_logger

# Logger setup
try:
    logger = setup_logger()
except Exception:
    logger = None


def get_document_percentage_stats(application_id: str, start_date: str, end_date: str):
    """
    Fetches document-wise accuracy statistics for a given application ID and date range.
    
    Args:
        application_id (str): The application ID to filter records.
        start_date (str): Start date (format: YYYY-MM-DD).
        end_date (str): End date (format: YYYY-MM-DD).
    
    Returns:
        list: A list of dictionaries containing document type statistics.
    """
    try:
        db: Session = SessionLocal()

        logger.info(
            f"Fetching document-wise average accuracy stats for application_id={application_id}, "
            f"start_date={start_date}, end_date={end_date}"
        )

        # Adjust start_date and end_date to include full day
        start_datetime = f"{start_date} 00:00:00"
        end_datetime = f"{end_date} 23:59:59"

        logger.info(f"Adjusted datetime range: start_datetime={start_datetime}, end_datetime={end_datetime}")

        # Filter condition
        filter_condition = and_(
            Feedback.created_on >= start_datetime,
            Feedback.created_on <= end_datetime,
            Feedback.application_id == application_id,
            Feedback.feedback_source == 'IDP'
        )

        # ✅ Fixed CASE syntax
        stats = db.query(
            Feedback.document_type.label("documentType"),
            func.avg(Feedback.docswise_avg_accuracy).label("averageAccuracy"),
            func.count(Feedback.feedback_id).label("totalSampleSize"),
            func.sum(case([(Feedback.docswise_avg_accuracy >= 81, 1)], else_=0)).label("greaterThan81"),
            func.sum(case([(and_(Feedback.docswise_avg_accuracy >= 71, Feedback.docswise_avg_accuracy < 81), 1)], else_=0)).label("range71to80"),
            func.sum(case([(and_(Feedback.docswise_avg_accuracy >= 50, Feedback.docswise_avg_accuracy < 71), 1)], else_=0)).label("range50to70"),
            func.sum(case([(Feedback.docswise_avg_accuracy < 50, 1)], else_=0)).label("lessThan50")
        ).filter(filter_condition).group_by(Feedback.document_type).all()

        # Build result
        result = []
        doc_type_reports = []

        for stat in stats:
            total_docs = stat.totalSampleSize or 0
            doc_type_reports.append({
                "documentType": stat.documentType,
                "averageAccuracy": round(stat.averageAccuracy, 2) if stat.averageAccuracy else 0,
                "totalSampleSize": total_docs,
                "greaterThan81": stat.greaterThan81,
                "range71to80": stat.range71to80,
                "range50to70": stat.range50to70,
                "lessThan50": stat.lessThan50,
                "accuracyRate": {
                    "greaterThan81Pct": round((stat.greaterThan81 / total_docs) * 100, 2) if total_docs else 0,
                    "between71to80Pct": round((stat.range71to80 / total_docs) * 100, 2) if total_docs else 0,
                    "between50to70Pct": round((stat.range50to70 / total_docs) * 100, 2) if total_docs else 0,
                    "lessThan50Pct": round((stat.lessThan50 / total_docs) * 100, 2) if total_docs else 0,
                },
            })

        result.append({
            "applicationId": application_id,
            "docTypeReport": doc_type_reports
        })

        logger.info(f"Successfully fetched stats for application_id={application_id}")
        return result

    except Exception as e:
        logger.error(f"Error in get_document_percentage_stats: {str(e)}")
        return {"error": str(e)}

    finally:
        db.close()
