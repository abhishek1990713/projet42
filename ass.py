from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class FeedbackResponse(BaseModel):
    id: int
    application_id: str
    correlation_id: str
    soeid: str
    authorization_coin_id: str
    feedback_json: Dict
    document_id: Optional[str] = None   # Allow None
    file_id: Optional[str] = None       # Allow None
    created_at: datetime

    class Config:
        orm_mode = True
