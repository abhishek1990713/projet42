payload = {
    "content": {   # 👈 wrap inside "content"
        "extractedData": {
            "Bo_Name": "Brazilian Palm Tree LTD",
            "Country_of_residence": "Norway",
            "Pay Year": 2025,
            "Market": "Finland",
            "Address": "0107 OSLO, NORWAY",
            "law Article": "Article 4 paragraph 1 of the Tax Convention",
            "Signature": "SIGMOM",
            "Seal": "The Norwegian Tax Admin",
            "Our Reference": "2024/5570364",
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
}
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
    Accepts the entire request body as a JSON object.
    No 'content' key is required.
    """

    __root__: Dict[str, Any]  # Accepts any JSON structure

    @validator("__root__", pre=True, always=True)
    def validate_content(cls, v):
        """
        Validate that the request body is a proper JSON object (dict).
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
