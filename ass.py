@app.get("/fetch_feedback", response_model=List[Dict[str, Any]])
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    start_day: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_day: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    """
    Fetch only 'file_id', 'document_id', and the nested 'field_feedback' 
    and 'document_feedback' from feedback_response for a given application_id 
    within a date range.
    """
    try:
        # Validate date format
        try:
            datetime.strptime(start_day, "%Y-%m-%d")
            datetime.strptime(end_day, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

        start_datetime = f"{start_day} 00:00:00"
        end_datetime = f"{end_day} 23:59:59"

        # Query only required columns
        results = (
            db.query(
                Feedback.file_id,
                Feedback.document_id,
                Feedback.feedback_response
            )
            .filter(Feedback.application_id == application_id)
            .filter(Feedback.created_at.between(start_datetime, end_datetime))
            .order_by(Feedback.id.asc())
            .all()
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No feedback records found for the given application_id in the date range",
            )

        # Extract file_id, document_id, and filtered feedback fields
        response_data = []
        for file_id, document_id, feedback_json in results:
            filtered = {
                "file_id": file_id,
                "document_id": document_id,
                "field_feedback": feedback_json.get("field_feedback", {}),
                "document_feedback": feedback_json.get("document_feedback", {}),
            }
            response_data.append(filtered)

        if logger:
            logger.info(
                f"Fetched {len(results)} filtered feedback records for application_id={application_id}"
            )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error fetching filtered feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
