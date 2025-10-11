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
