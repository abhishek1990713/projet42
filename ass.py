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
