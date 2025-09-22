
import logging
from fastapi import FastAPI, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
import uvicorn

from . import models, schemas
from .database import engine, get_db, DB_NAME
from .setup_log import setup_logger
from .constants import *

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception:
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

# ---------------- FastAPI App ----------------
app = FastAPI(title="Feedback API")

# ---------------- Startup Event ----------------
@app.on_event("startup")
def create_db_and_tables():
    """
    Create the database and tables at application startup if they do not exist.
    """
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info(DB_TABLES_CREATED)
    except Exception as e:
        logger.error(DB_INIT_FAILURE.format(e))
        raise RuntimeError(DB_INIT_FAILURE_RUNTIME) from e


# ---------------- Upload Feedback Endpoint ----------------
@app.post(UPLOAD_JSON, response_model=schemas.FeedbackResponse, status_code=status.HTTP_201_CREATED)
def upload_json(
    payload: dict,
    db: Session = Depends(get_db),
    x_correlation_id: str = Header(..., alias="x-correlation-id"),
    x_application_id: str = Header(..., alias="x-application-id"),
    x_soeid: str = Header(..., alias="x-soeid"),
    x_authorization_coin: str = Header(..., alias="X-Authorization-Coin")
):
    """
    Endpoint to save JSON feedback data along with headers.
    The full request body is stored in feedback_json.
    """
    try:
        if not payload:
            logger.warning(INVALID_JSON_LOG)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID_JSON_MSG,
            )

        # ---------------- Insert into DB ----------------
        db_feedback = models.Feedback(
            correlation_id=x_correlation_id,
            application_id=x_application_id,
            soeid=x_soeid,
            authorization_coin=x_authorization_coin,
            feedback_json=payload,
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        logger.info(DB_INSERT_SUCCESS_LOG)

        return db_feedback

    except HTTPException as http_exc:
        logger.error(HTTP_EXCEPTION_LOG.format(http_exc.detail))
        raise http_exc
    except Exception as e:
        db.rollback()
        logger.error(DB_OPERATION_FAILED_LOG.format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR_MSG.format(str(e)),
        )


# ---------------- Main Entry Point ----------------
if __name__ == "__main__":
    uvicorn.run(
        UVICORN_APP,
        host=UVICORN_HOST,
        port=UVICORN_PORT,
        log_level=UVICORN_LOG_LEVEL,
        reload=UVICORN_RELOAD,
    )
