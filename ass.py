@app.get("/fetch_feedback", response_model=List[Dict[str, Any]])
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    start_day: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_day: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    """
    Fetch only the feedback_response column for a given application_id 
    within a date range.
    """
    try:
        # Validate date format
        try:
            datetime.strptime(start_day, "%Y-%m-%d")
            datetime.strptime(end_day, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        start_datetime = f"{start_day} 00:00:00"
        end_datetime = f"{end_day} 23:59:59"

        # Query only feedback_response column
        results = (
            db.query(Feedback.feedback_response)
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

        # Extract feedback_response from tuples
        response_data = [r[0] for r in results]

        if logger:
            logger.info(
                f"Fetched {len(results)} feedback_response records for application_id={application_id}"
            )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error fetching feedback_response: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
