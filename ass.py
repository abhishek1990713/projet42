@app.post("/feedback_service", status_code=status.HTTP_201_CREATED)
async def upload_json(
    request: Request,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    x_correlation_id: str = Header(...),
    x_application_id: str = Header(...),
    x_created_by: str = Header(...),
    x_document_id: str = Header(...),
    x_file_id: str = Header(...),
    x_authorization_coin: str = Header(...),
    x_feedback_source: str = Header(...)
):
    """
    Endpoint to insert feedback data into the database.
    Validates input, calculates feedback stats, and stores JSON feedback.
    """

    try:
        # -------------------------------------------------------
        # Step 1: Extract document type and feedback section
        # -------------------------------------------------------
        document_type = payload.get("Document_type", "Unknown")  # ✅ Extract from payload
        feedback_section = payload.get("feedback", {})

        # -------------------------------------------------------
        # Step 2: Calculate feedback stats
        # -------------------------------------------------------
        stats = calculate_feedback_stats(feedback_section)

        # -------------------------------------------------------
        # Step 3: Validate with schema
        # -------------------------------------------------------
        feedback_data = schemas.FeedbackResponse(
            id=0,
            correlation_id=x_correlation_id,
            application_id=x_application_id,
            document_id=x_document_id,
            file_id=x_file_id,
            authorization_coin_id=x_authorization_coin,
            feedback_response=payload,
            feedback_source=x_feedback_source,
            created_by=x_created_by,
            created_on=datetime.now(),
            field_count=stats["field_count"],
            positive_count=stats["positive_count"],
            negative_count=stats["negative_count"],
            percentage=stats["percentage"],
            document_type=document_type   # ✅ Added here
        )

        if logger:
            logger.info(VALIDATION_SUCCESS_LOG)

    except Exception as e:
        if logger:
            logger.error(VALIDATION_ERROR_LOG.format(e), exc_info=True)
        raise HTTPException(status_code=400, detail=VALIDATION_FAILED_MSG)

    # -------------------------------------------------------
    # Step 4: Insert feedback into the database
    # -------------------------------------------------------
    try:
        db_feedback = Feedback(
            correlation_id=x_correlation_id,
            created_by=x_created_by,
            application_id=x_application_id,
            document_id=x_document_id,
            file_id=x_file_id,
            authorization_coin_id=x_authorization_coin,
            feedback_source=x_feedback_source,
            feedback_response=payload,
            field_count=stats["field_count"],
            positive_count=stats["positive_count"],
            negative_count=stats["negative_count"],
            percentage=stats["percentage"],
            document_type=document_type   # ✅ Insert into DB
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        if logger:
            logger.info(DB_INSERT_SUCCESS_LOG)

        return {
            "message": DATA_INSERTED,
            SUCCESS: True,
            "details": {
                "id": db_feedback.id,
                "correlation_id": db_feedback.correlation_id,
                "application_id": db_feedback.application_id,
                "created_by": db_feedback.created_by,
                "document_id": db_feedback.document_id,
                "feedback_source": db_feedback.feedback_source,
                "file_id": db_feedback.file_id,
                "document_type": db_feedback.document_type,   # ✅ Shown in response
                "field_count": db_feedback.field_count,
                "positive_count": db_feedback.positive_count,
                "negative_count": db_feedback.negative_count,
                "percentage": db_feedback.percentage
            }
        }

    except Exception as e:
        db.rollback()
        if logger:
            logger.error(DB_OPERATION_FAILED_LOG.format(e), exc_info=True)
        raise HTTPException(status_code=500, detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e)))





from sqlalchemy.orm import Session
from sqlalchemy import func, case
from db.models import FeedbackResponse   # ORM model class (update import path if needed)
from logger_config import logger


def get_document_percentage_stats(db: Session, document_type: str = None):
    """
    Function to calculate feedback percentage distribution per document type.
    Filters by 'document_type' if provided.
    Returns:
      [
        {
          "document_type": "passport",
          "total_documents": 25,
          "greater_than_81": 10,
          "range_71_to_80": 6,
          "range_50_to_70": 7,
          "less_than_50": 2,
          "summary_percentage": {
            ">81%": 40.0,
            "71–80%": 24.0,
            "50–70%": 28.0,
            "<50%": 8.0
          }
        }
      ]
    """
    try:
        logger.info("Fetching document percentage statistics...")

        # Base query
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

        # Apply filter if document_type is passed in header
        if document_type:
            logger.info(f"Filtering statistics for document_type: {document_type}")
            query = query.filter(FeedbackResponse.document_type == document_type)

        # Group by document_type to get stats for each type
        query = query.group_by(FeedbackResponse.document_type)
        results = query.all()

        # If no data found
        if not results:
            logger.warning("No records found for given document_type or dataset is empty")
            return []

        # Prepare structured response
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
        return []
