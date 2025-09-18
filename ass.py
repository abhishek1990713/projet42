# schemas.py
from pydantic import BaseModel
from typing import Dict, Any, Optional

class FeedbackBase(BaseModel):
    application_id: str
    consumer_id: str
    feedback_json: Dict[str, Any]

class FeedbackCreate(FeedbackBase):
    authorization_coin_id: str

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None   # ✅ FIXED

    class Config:
        orm_mode = True
