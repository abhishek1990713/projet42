import logging
from typing import Dict, Any

from fastapi import HTTPException, status
from pydantic import BaseModel, validator

from exceptions.setup_log import setup_logger
from constant.constants import (
    INVALID_JSON_LOG,
    VALIDATION_SUCCESS_LOG,
    VALIDATION_ERROR_LOG,
    UNEXPECTED_VALIDATION_ERROR_LOG,
    INVALID_JSON_MSG,
    UNEXPECTED_VALIDATION_ERROR_MSG,
)

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception as e:
    logger = None
    print(f"Logger setup failed: {e}")


class FeedbackCreate(BaseModel):
    """
    Pydantic model for feedback creation.
    Only `content` is passed in the request body.
    All other fields come from request headers.
    """

    content: Dict[str, Any]

    @validator("content", pre=True, always=True)
    def validate_content_json(cls, v):
        """
        Validate that content is a proper JSON object (dict).
        Logs success/failure.
        """
        try:
            if not isinstance(v, dict):
                if logger:
                    logger.error(INVALID_JSON_LOG)
                raise ValueError(INVALID_JSON_MSG)

            if logger:
                logger.info(VALIDATION_SUCCESS_LOG)
            return v

        except ValueError as e:
            if logger:
                logger.error(VALIDATION_ERROR_LOG.format(e))
            raise

        except Exception as e:
            if logger:
                logger.error(UNEXPECTED_VALIDATION_ERROR_LOG.format(str(e)))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e)),
            )


class FeedbackResponse(BaseModel):
    """
    Pydantic model for feedback response.
    Maps ORM table columns to response fields.
    """

    id: int
    application_id: str
    correlation_id: str
    content: Dict[str, Any]
    soeid: str
    authorization_coin_id: str
    created_at: Any

    class Config:
        orm_mode = True


import logging
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import FeedbackCreate

# ---------------- Logger Setup ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/feedback/")
def create_feedback(
    feedback_data: FeedbackCreate,
    request: Request,
    x_correlation_id: str = Header(..., alias="x-correlation-id"),
    x_application_id: str = Header(..., alias="x-application-id"),
    x_soeid: str = Header(..., alias="x-soeid"),
    x_authorization_coin: str = Header(..., alias="x-authorization-coin"),
    db: Session = Depends(get_db),
):
    """
    API endpoint to store feedback data into PostgreSQL.
    Stores the entire request body as JSON in the 'content' column.
    """

    try:
        # Extract raw request body JSON
        payload = feedback_data.__root__

        db_feedback = models.Feedback(
            application_id=x_application_id,
            correlation_id=x_correlation_id,
            content=payload,   # ✅ Store the whole request body
            soeid=x_soeid,
            authorization_coin_id=x_authorization_coin,
        )

        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)

        logger.info(f"Feedback stored successfully with ID {db_feedback.id}")

        return {"message": "Feedback stored successfully", "id": db_feedback.id}

    except Exception as e:
        logger.error(f"DB Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")


import requests
import json

url = "http://127.0.0.1:8000/feedback/"

headers = {
    "x-correlation-id": "test-corr-id-123",
    "x-soeid": "test-soeid-456",
    "x-authorization-coin": "auth-coin-789",
    "x-application-id": "app-id-001",
    "Content-Type": "application/json"
}

payload = {
    "extractedData": {
        "Bo_Name": "Brazilian Palm Tree LTD",
        "Country_of_residence": "Norway",
        "Pay Year": 2025,
        "Market": "Finland",
        "Address": "0107 OSLO, NORWAY",
        "law Article": "Article 4 paragraph 1 of the Tax Convention",
        "Signature": "SIGMOM",
        "Seal": "The Norwegian Tax Admin",
        "Our Reference": "2824/5570364",
        "Tax_Identification_number": "974761076",
        "postal address": "P.O. Box 9288 Grenland 0134 Oslo",
        "Document Validation": ""
    },
    "feedback": {
        "Bo_Name": {"status": "thumbs_up"},
        "Country_of_residence": {"status": "thumbs_down", "comments": "wfefngn"},
        "Pay Year": {"status": "thumbs_down", "comments": "th"}
    }
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
