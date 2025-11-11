"""
validation.py

Handles 'VALIDATION' input source payloads for rule-based validation feedback.
Transforms the data into a standardized structure for storage and response.
"""

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from logger_config import setup_logger
from constant import (
    UNKNOWN,
    VALIDATION_SUCCESS_MSG,
    VALIDATION_ERROR_MSG
)

logger = setup_logger()


def handle_validation_json(
    request: Request,
    payload: dict,
    db: Session,
    x_correlation_id: str,
    x_application_id: str,
    x_created_by: str,
    x_document_id: str,
    x_file_id: str,
    x_authorization_coin: str,
    x_feedback_source: str,
    x_input_source: str
):
    """
    Handles validation input data (from LLM or other automated validators).
    Extracts validation info, converts it into structured feedback,
    and saves it in the database.
    """

    try:
        if logger:
            logger.info(
                f"[handle_validation_json()] [SOEID: {x_created_by}] "
                f"[Correlation ID: {x_correlation_id}] [Document ID: {x_document_id}] - Processing VALIDATION input"
            )

        # ✅ Extract validation data
        validation_data = payload.get("validationData")
        if not validation_data:
            raise ValueError("Missing 'validationData' in payload")

        # Extract fields
        mode = validation_data.get("mode", UNKNOWN)
        raw_status = validation_data.get("status", UNKNOWN)
        comment = validation_data.get("comment", "")
        rule_id = validation_data.get("rule_id", UNKNOWN)

        # Extract response metadata
        response_metadata = validation_data.get("response_metadata", {})
        perf_metrics = response_metadata.get("performance_metrics", {})

        memory_peak_usage_mb = perf_metrics.get("memory_peak_usage_mb", 0.0)
        execution_time_seconds = perf_metrics.get("execution_time_seconds", 0.0)
        validation_status = perf_metrics.get("validation_status", raw_status)

        # ✅ Construct field_feedback (as dict instead of list)
        field_feedback = {
            rule_id: {
                "comment": comment,
                "status": validation_status
            }
        }

        # ✅ Construct final record for DB
        validation_record = {
            "application_id": x_application_id,
            "document_id": x_document_id,
            "file_id": x_file_id,
            "created_by": x_created_by,
            "mode": mode,
            "status": validation_status,
            "rule_id": rule_id,
            "field_feedback": field_feedback,
            "memory_peak_usage_mb": memory_peak_usage_mb,
            "execution_time_seconds": execution_time_seconds,
            "feedback_source": x_feedback_source,
            "input_source": x_input_source
        }

        # ✅ Example DB save (replace with ORM model if needed)
        db.add(validation_record)
        db.commit()

        if logger:
            logger.info(
                f"[handle_validation_json()] [Document ID: {x_document_id}] - Validation data saved successfully."
            )

        # ✅ Final API response
        return {
            "document_id": x_document_id,
            "rule_id": rule_id,
            "status": validation_status,
            "message": VALIDATION_SUCCESS_MSG,
            "field_feedback": field_feedback
        }

    except Exception as e:
        db.rollback()
        if logger:
            logger.exception(
                f"[handle_validation_json()] [Document ID: {x_document_id}] - Error: {str(e)}"
            )
        raise HTTPException(status_code=500, detail=VALIDATION_ERROR_MSG)
