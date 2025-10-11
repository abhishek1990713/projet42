from sqlalchemy.orm import Session
from sqlalchemy import func, case
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


def get_document_percentage_stats(db: Session, document_type: str = None):
    """
    Calculate feedback percentage distribution per document type.
    Filters by 'document_type' if provided.
    """
    try:
        logger.info("Fetching document percentage statistics...")

        query = db.query(
            FeedbackResponse.document_type,
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

        if document_type:
            logger.info(f"Filtering statistics for document_type: {document_type}")
            query = query.filter(FeedbackResponse.document_type == document_type)

        query = query.group_by(FeedbackResponse.document_type)
        results = query.all()

        if not results:
            logger.warning("No records found for given document_type or dataset is empty")
            return []

        response_data = []
        for row in results:
            total_docs = row.total_docs or 0
            data = {
                "document_type": row.document_type,
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
        return []from fastapi import FastAPI, Depends, Header
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from db.database import get_db
from document_stats import get_document_percentage_stats, get_all_document_types
from logger_config import logger


# -----------------------------------------------------------
# FastAPI app initialization
# -----------------------------------------------------------
app = FastAPI(title="Document Statistics API")

# Enable CORS (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------
# GET 1️⃣ : Document Stats (filtered by header document_type)
# -----------------------------------------------------------
@app.get("/document_stats", summary="Get feedback percentage stats by document type")
def document_stats(
    document_type: str = Header(None, description="Document type to filter stats (e.g., passport, license)"),
    db: Session = Depends(get_db)
):
    """
    Fetch document percentage statistics from FeedbackResponse table.

    Header:
      document_type: optional — filters data by document type.
    """
    logger.info(f"Received /document_stats request for document_type: {document_type or 'ALL'}")
    return get_document_percentage_stats(db, document_type)


# -----------------------------------------------------------
# GET 2️⃣ : Get All Document Types
# -----------------------------------------------------------
@app.get("/document_types", summary="Get all distinct document types")
def document_types(db: Session = Depends(get_db)):
    """
    Returns all distinct document types stored in the database.
    Example Response:
      ["passport", "driving_license", "residence_certificate"]
    """
    logger.info("Fetching all distinct document types...")
    return get_all_document_types(db)


# -----------------------------------------------------------
# Run the FastAPI server
# -----------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8093, reload=True)

