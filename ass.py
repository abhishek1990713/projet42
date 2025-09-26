from fastapi import FastAPI, HTTPException, Depends, Header, status, Body
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Feedback
from service import schemas
from exceptions.setup_log import setup_logger
from constant.constants import *
from datetime import datetime
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Logger setup
try:
    logger = setup_logger()
except Exception:
    logger = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_json", status_code=status.HTTP_200_OK)
async def upload_json(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    correlation_id: str = Header(...),
    app_id: str = Header(...),
):
    # Validate input
    try:
        feedback_data = schemas.FeedbackCreate(feedback=payload)  # changed key
        if logger:
            logger.info(VALIDATION_SUCCESS_LOG)
    except Exception as e:
        if logger:
            logger.error(VALIDATION_ERROR_LOG.format(e))
        raise HTTPException(status_code=400, detail=VALIDATION_FAILED_MSG)

    # Update feedback in existing row
    try:
        db_feedback = db.query(Feedback).filter(
            Feedback.correlation_id == correlation_id,
            Feedback.app_id == app_id
        ).first()

        if not db_feedback:
            raise HTTPException(
                status_code=404,
                detail=f"No record found for correlation_id={correlation_id} and app_id={app_id}"
            )

        db_feedback.feedback = payload  # updated column
        db_feedback.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_feedback)

        if logger:
            logger.info(DB_UPDATE_SUCCESS_LOG.format(app_id, correlation_id))

        return {
            SUCCESS: True,
            "message": DATA_UPDATED,
            "details": {
                "audit_id": db_feedback.audit_id,
                "app_id": db_feedback.app_id,
                "correlation_id": db_feedback.correlation_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        if logger:
            logger.error(DB_OPERATION_FAILED_LOG.format(e))
        raise HTTPException(status_code=500, detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e)))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8092, reload=True)
