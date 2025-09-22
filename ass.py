
import logging
from typing import Any, Dict

from fastapi import HTTPException, status
from pydantic import BaseModel, RootModel, field_validator

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


# ------------------ Request Model ------------------
class FeedbackCreate(RootModel[Dict[str, Any]]):
    """
    Root model for feedback creation.
    Accepts the entire request body as a JSON object.
    """

    @field_validator("*", mode="before")
    def validate_content(cls, v):
        if not isinstance(v, dict):
            if logger:
                logger.error(INVALID_JSON_LOG)
            raise ValueError(INVALID_JSON_MSG)
        if logger:
            logger.info(VALIDATION_SUCCESS_LOG)
        return v


# ------------------ Response Model ------------------
class FeedbackResponse(BaseModel):
    """
    Normal Pydantic model for feedback response.
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
