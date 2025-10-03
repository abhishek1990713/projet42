Subject: 
@app.get("/fetch_feedback")
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    document_id: str = Query(..., description="Document ID"),
    start_day: str = Query(..., description="Date in YYYY-MM-DD format"),
    end_day: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    """Fetch only feedback_json for given filters"""

    try:
        # Validate and parse dates
        start_date = parse_date(start_day)
        end_date = parse_date(end_day)

        start_datetime = f"{start_date.strftime('%Y-%m-%d')} 00:00:00"
        end_datetime = f"{end_date.strftime('%Y-%m-%d')} 23:59:59"

        # Query only feedback_json column
        results = (
            db.query(Feedback.feedback_json)
            .filter(Feedback.application_id == application_id)
            .filter(Feedback.document_id == document_id)
            .filter(Feedback.created_at.between(start_datetime, end_datetime))
            .order_by(Feedback.id.asc())
            .all()
        )

        # SQLAlchemy returns list of tuples, so unwrap them
        feedback_only = [row[0] for row in results]

        return feedback_only

    except Exception as e:
        if logger:
            logger.error(f"Error fetching feedback_json: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

