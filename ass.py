from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from .database import Base

class Feedback(Base):
    """
    Feedback table model.
    Stores request headers as separate columns and the full request body in feedback_json.
    """

    __tablename__ = "feedback"   # Table name in DB

    id = Column(Integer, primary_key=True, index=True)  # Auto-increment primary key
    correlation_id = Column(String, nullable=False, index=True)  # From header: x-correlation-id
    application_id = Column(String, nullable=False, index=True)  # From header: x-application-id
    soeid = Column(String, nullable=False, index=True)  # From header: x-soeid
    authorization_coin = Column(String, nullable=False)  # From header: X-Authorization-Coin
    feedback_json = Column(JSON, nullable=False)  # Full request body (extractedData + feedback)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Auto timestamp
