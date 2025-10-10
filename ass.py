from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import SessionLocal
from db.models import FeedbackResponse  # your ORM model class
from logger_config import logger


def get_document_percentage_stats():
    """
    Function to calculate:
      - total number of documents
      - how many have percentage > 81
      - 71–80
      - 50–70
      - < 50
    Returns a dictionary with the counts and percentage distribution.
    """
    try:
        db: Session = SessionLocal()

        logger.info("Fetching document percentage statistics...")

        total_docs = db.query(func.count(FeedbackResponse.id)).scalar()

        above_81 = db.query(func.count()).filter(FeedbackResponse.percentage > 81).scalar()
        range_71_80 = db.query(func.count()).filter(
            FeedbackResponse.percentage >= 71, FeedbackResponse.percentage <= 80
        ).scalar()
        range_50_70 = db.query(func.count()).filter(
            FeedbackResponse.percentage >= 50, FeedbackResponse.percentage <= 70
        ).scalar()
        below_50 = db.query(func.count()).filter(FeedbackResponse.percentage < 50).scalar()

        logger.info(f"Total documents: {total_docs}")
        logger.info(f">81%: {above_81}, 71–80%: {range_71_80}, 50–70%: {range_50_70}, <50%: {below_50}")

        result = {
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
            }
        }

        return result

    except Exception as e:
        logger.error(f"Error in get_document_percentage_stats: {str(e)}")
        return {"error": str(e)}

    finally:
        db.close()


if __name__ == "__main__":
    stats = get_document_percentage_stats()
    print(stats)
