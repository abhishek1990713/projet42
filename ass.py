from fastapi import FastAPI, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from document_stats import get_document_percentage_stats
from feedbackreport import feedback_report
from db.database import get_db
from logger_config import logger
import uvicorn

app = FastAPI(title="Feedback Stats API")


@app.get("/feedback/stats", tags=["Feedback Stats"])
def fetch_feedback_stats(
    application_id: str = Header(None),
    start_date: str = Header(None),
    end_date: str = Header(None)
):
    """
    GET endpoint to fetch document percentage statistics by application_id and date range.

    Headers:
        - application_id: (str) Application ID to filter results.
        - start_date: (str, format YYYY-MM-DD)
        - end_date: (str, format YYYY-MM-DD)
    """
    try:
        if not application_id or not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail="Headers 'application_id', 'start_date', and 'end_date' are required."
            )

        logger.info(
            f"Received request for application_id={application_id}, start_date={start_date}, end_date={end_date}"
        )
        result = get_document_percentage_stats(application_id, start_date, end_date)

        if not result or (isinstance(result, dict) and "error" in result):
            raise HTTPException(
                status_code=404,
                detail=f"No records found for application_id={application_id} within given date range."
            )

        return result

    except HTTPException as http_err:
        logger.warning(f"HTTP error: {http_err.detail}")
        raise http_err

    except Exception as e:
        logger.error(f"Unexpected error in fetch_feedback_stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/feedback/report", tags=["Feedback Report"])
def fetch_feedback_report(
    application_id: str = Header(None),
    start_date: str = Header(None),
    end_date: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    GET endpoint to fetch detailed feedback report for given application_id and date range.

    Headers:
        - application_id: (str) Application ID to filter results.
        - start_date: (str, format YYYY-MM-DD)
        - end_date: (str, format YYYY-MM-DD)
    """
    try:
        if not application_id or not start_date or not end_date:
            raise HTTPException(
                status_code=400,
                detail="Headers 'application_id', 'start_date', and 'end_date' are required."
            )

        logger.info(
            f"Generating feedback report for application_id={application_id}, "
            f"start_date={start_date}, end_date={end_date}"
        )

        result = feedback_report(application_id, start_date, end_date, db)

        if not result or (isinstance(result, dict) and "error" in result):
            raise HTTPException(
                status_code=404,
                detail=f"No feedback report found for application_id={application_id} within given date range."
            )

        return result

    except HTTPException as http_err:
        logger.warning(f"HTTP error in feedback report: {http_err.detail}")
        raise http_err

    except Exception as e:
        logger.error(f"Unexpected error in fetch_feedback_report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    # Run the FastAPI app on port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
