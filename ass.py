from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any

from db.database import get_db
from document_stats import get_all_document_types, get_document_percentage_stats
from logger_config import logger

app = FastAPI(
    title="Document Statistics API",
    description="Provides feedback and document performance analytics",
    version="1.0.0"
)


@app.get("/document/types", response_model=List[str])
def fetch_document_types(db: Session = Depends(get_db)):
    """
    API Endpoint: Get all available document types.
    ----------------------------------------------------
    **Purpose:**  
    Returns a list of unique document types stored in the feedback database.

    **Example Response:**
    ```json
    ["passport", "driving_license", "residence_certificate"]
    ```
    """
    try:
        logger.info("API call: /document/types")
        types = get_all_document_types(db)
        if not types:
            logger.warning("No document types found in the database.")
        return types
    except Exception as e:
        logger.error(f"Error fetching document types: {str(e)}", exc_info=True)
        return []


@app.get("/document/stats")
def fetch_document_stats(
    db: Session = Depends(get_db),
    application_id: Optional[str] = Query(None, description="Filter results by application_id"),
    start_date: Optional[str] = Query(None, description="Start date in 'YYYY-MM-DD' format"),
    end_date: Optional[str] = Query(None, description="End date in 'YYYY-MM-DD' format")
):
    """
    API Endpoint: Get document percentage statistics.
    ----------------------------------------------------
    **Purpose:**  
    Retrieves aggregated feedback percentage distribution per application ID,
    filtered optionally by date range.

    **Query Parameters:**
    - `application_id`: Optional. Filter by specific application.
    - `start_date`: Optional. Include records from this date.
    - `end_date`: Optional. Include records up to this date.

    **Response Example:**
    ```json
    [
      {
        "application_id": "APP123",
        "total_documents": 100,
        "greater_than_81": 40,
        "range_71_to_80": 30,
        "range_50_to_70": 20,
        "less_than_50": 10,
        "summary_percentage": {
          ">81%": 40.0,
          "71–80%": 30.0,
          "50–70%": 20.0,
          "<50%": 10.0
        }
      }
    ]
    ```
    """
    try:
        logger.info(
            f"API call: /document/stats with params -> application_id={application_id}, start_date={start_date}, end_date={end_date}"
        )

        # Validate date inputs
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                logger.error(f"Invalid start_date format: {start_date}")
                return {"error": "Invalid start_date format. Use YYYY-MM-DD."}

        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                logger.error(f"Invalid end_date format: {end_date}")
                return {"error": "Invalid end_date format. Use YYYY-MM-DD."}

        # Fetch data from document_stats.py
        result = get_document_percentage_stats(
            db=db,
            application_id=application_id,
            start_date=start_date,
            end_date=end_date
        )

        if not result:
            logger.warning("No statistics found for the provided filters.")
            return {"message": "No data available for the provided filters."}

        logger.info("Document statistics fetched successfully.")
        return result

    except Exception as e:
        logger.error(f"Error in /document/stats: {str(e)}", exc_info=True)
        return {"error": str(e)}
