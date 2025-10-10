from typing import Any, Dict, Optional
from pydantic import BaseModel

class FeedbackResponse(BaseModel):
    id: int
    correlation_id: str
    application_id: str
    document_id: Optional[str] = None
    file_id: Optional[str] = None
    authorization_coin_id: str
    feedback_response: Dict[str, Any]
    feedback_source: Optional[str] = None
    created_by: Optional[str] = None
    created_on: Any

    field_count: Optional[int] = 0      # ✅ Default to 0
    positive_count: Optional[int] = 0   # ✅ Default to 0
    negative_count: Optional[int] = 0   # ✅ Default to 0
    percentage: Optional[float] = 0.0   # ✅ Default to 0.0

    class Config:
        orm_mode = True


feedback_data = schemas.FeedbackResponse(
    id=0,
    correlation_id=x_correlation_id,
    application_id=x_application_id,
    document_id=x_document_id,
    file_id=x_file_id,
    authorization_coin_id=x_authorization_coin,
    feedback_response=payload,
    feedback_source=x_feedback_source,
    created_by=x_created_by,
    created_on=datetime.now(),
    field_count=stats.get("field_count", 0),
    positive_count=stats.get("positive_count", 0),
    negative_count=stats.get("negative_count", 0),
    percentage=stats.get("percentage", 0.0)
)
