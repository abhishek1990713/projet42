from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class FeedbackResponse(BaseModel):
    audit_id: int
    consumer_coin: Optional[str]
    app_id: str
    app_name: Optional[str]
    usecase_config_id: Optional[str]
    request: Optional[Dict[str, Any]]
    response: Optional[Dict[str, Any]]
    feedback: Dict[str, Any]  # renamed from feedback_json
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]
    correlation_id: str

    class Config:
        orm_mode = True

class FeedbackCreate(BaseModel):
    feedback: Dict[str, Any]  # renamed from feedback_json
