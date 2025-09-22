# schemas.py

import json
import logging
from typing import Dict, Any

from fastapi import HTTPException, status
from pydantic import BaseModel, validator

from constant.constants import *
from exceptions.setup_log import setup_logger

# ---------------- Logger Setup ----------------
try:
    logger = setup_logger()
except Exception:
    logger = None


class FeedbackCreate(BaseModel):
    """
    Pydantic model for creating feedback.
    Fields map directly to table columns:
    - Application_Id
    - correlation_id
    - content (JSON)
    - soeid
    - authorization_coin_id
    """
    Application_Id: str
    correlation_id: str
    content: Dict[str, Any]
    soeid: str
    authorization_coin_id: str

    @validator("content", pre=True, always=True)
    def validate_content_json(cls, v):
        """
        Validate that content is a proper JSON object (dict).
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
                logger.error(UNEXPECTED_VALIDATION_ERROR_LOG.format(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=UNEXPECTED_VALIDATION_ERROR_MSG.format(str(e))
            )


class FeedbackResponse(BaseModel):
    """
    Pydantic model for feedback response.
    Maps ORM table columns to response fields.
    """
    id: int
    Application_Id: str
    correlation_id: str
    content: Dict[str, Any]
    soeid: str
    authorization_coin_id: str
    created_at: Any

    class Config:
        # Allows reading data directly from ORM objects
        orm_mode = True
