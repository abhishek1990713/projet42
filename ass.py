@app.get("/fetch_feedback")
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    Start_day: str = Query(..., description="Start date in YYYY-MM-DD format"),
    End_day: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    """
    Fetch feedback records for a given application_id within a date range.
    Only returns application_id and document_id in the response.
    """
    try:
        # Validate date format
        try:
            datetime.strptime(Start_day, "%Y-%m-%d")
            datetime.strptime(End_day, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        start_datetime = f"{Start_day} 00:00:00"
        end_datetime = f"{End_day} 23:59:59"

        # Fetch only required columns
        results = (
            db.query(Feedback.application_id, Feedback.document_id)
            .filter(Feedback.application_id == application_id)
            .filter(Feedback.created_at.between(start_datetime, end_datetime))
            .all()
        )

        if not results:
            return {"status": "success", "message": "No records found."}

        # Convert to list of dicts
        response_data = [
            {"application_id": r.application_id, "document_id": r.document_id} for r in results
        ]

        return {"status": "success", "data": response_data}

    except Exception as e:
        if logger:
            logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching feedback.")
