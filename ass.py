from fastapi import FastAPI, HTTPException, Query
from typing import List
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uvicorn

app = FastAPI(title="Feedback API", version="1.0")

# Database config
DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USERNAME = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACЬ"
DB_NAME = "gssp_common"

DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Response model
class FeedbackResponse(BaseModel):
    id: int
    application_id: str
    correlation_id: str
    soeid: str
    authorization_coin_id: str
    created_at: str

# Endpoint
@app.get("/fetch_feedback", response_model=List[FeedbackResponse])
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    day: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """
    Fetch feedback records for a single day using full timestamp range.
    """
    try:
        session = SessionLocal()

        # Construct start and end timestamps for the day
        start_datetime = f"{day} 00:00:00"
        end_datetime = f"{day} 23:59:59"

        query = text("""
            SELECT id, application_id, correlation_id, soeid, authorization_coin_id, created_at
            FROM gssp_common.idp_feedback
            WHERE application_id = :application_id
              AND created_at BETWEEN :start_datetime AND :end_datetime
            ORDER BY id ASC;
        """)

        results = session.execute(
            query,
            {
                "application_id": application_id,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime
            }
        ).fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="No records found for the given application_id and date")

        feedback_list = []
        for row in results:
            feedback_list.append(
                FeedbackResponse(
                    id=row.id,
                    application_id=row.application_id,
                    correlation_id=row.correlation_id,
                    soeid=row.soeid,
                    authorization_coin_id=row.authorization_coin_id,
                    created_at=row.created_at.isoformat(),
                )
            )

        return feedback_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        session.close()

# Run server on port 8000
if __name__ == "__main__":
    uvicorn.run("fast:app", host="127.0.0.1", port=8000, reload=True)
