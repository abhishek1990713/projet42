@app.get("/fetch_feedback")
def fetch_feedback(
    application_id: str = Query(...),
    document_id: str = Query(...),
    start_day: str = Query(...),
    end_day: str = Query(...),
    db: Session = Depends(get_db),
):
