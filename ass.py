# app.py

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import date
import uvicorn

# ---------------- FastAPI App ----------------
app = FastAPI(title="Feedback API", version="1.0")

# ---------------- Database Config ----------------
DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USERNAME = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACЬ"
DB_NAME = "gssp_common"

DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------- Response Model ----------------
class FeedbackResponse(BaseModel):
    id: int
    application_id: str
    correlation_id: str
    content: dict
    soeid: str
    authorization_coin_id: str
    created_at: str


# ---------------- Endpoint ----------------
@app.get("/fetch_feedback", response_model=List[FeedbackResponse])
def fetch_feedback(
    application_id: str = Query(..., description="Application ID"),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
):
    """
    Fetch feedback data from PostgreSQL by application_id and created_at range.
    """
    try:
        session = SessionLocal()

        query = text("""
            SELECT id, application_id, correlation_id, content, soeid, authorization_coin_id, created_at
            FROM gssp_common.idp_feedback
            WHERE application_id = :application_id
              AND created_at BETWEEN :start_date AND :end_date
            ORDER BY id ASC;
        """)

        results = session.execute(
            query,
            {"application_id": application_id, "start_date": start_date, "end_date": end_date},
        ).fetchall()

        if not results:
            raise HTTPException(status_code=404, detail="No records found for given filters")

        feedback_list = []
        for row in results:
            feedback_list.append(
                FeedbackResponse(
                    id=row.id,
                    application_id=row.application_id,
                    correlation_id=row.correlation_id,
                    content=row.content,
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


# ---------------- Run Server ----------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
