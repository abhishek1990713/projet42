from fastapi import Body

@app.post(UPLOAD_JSON, status_code=status.HTTP_201_CREATED)
async def upload_json(
    payload: dict = Body(...),   # 👈 accept raw JSON
    correlation_id: str = Header(..., alias="x-correlation-id"),
    application_id: str = Header(..., alias="x-application-id"),
    soeid: str = Header(..., alias="x-soeid"),
    authorization_coin_id: str = Header(..., alias="X-Authorization-Coin"),
    db: Session = Depends(get_db)
):
    """
    Endpoint to upload a JSON payload and insert into DB.
    """
    try:
        # Validate JSON using schema
        feedback_data = schemas.FeedbackCreate(
            application_id=application_id,
            correlation_id=correlation_id,
            soeid=soeid,
            authorization_coin_id=authorization_coin_id,
            feedback_json=payload
        )

        db_feedback = models.Feedback(
            application_id=feedback_data.application_id,
            correlation_id=feedback_data.correlation_id,
            soeid=feedback_data.soeid,
            authorization_coin_id=feedback_data.authorization_coin_id,
            feedback_json=payload
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        return {
            "success": True,
            "message": DATA_INSERTED,
            "details": {
                "id": db_feedback.id,
                "application_id": db_feedback.application_id,
                "correlation_id": db_feedback.correlation_id,
                "soeid": db_feedback.soeid
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )
