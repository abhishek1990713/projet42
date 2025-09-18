# models.py
from sqlalchemy import Column, Integer, Text, JSON, TIMESTAMP, func
from db import Base

class Feedback(Base):
    """
    ORM model for Feedback table inside gssp_common schema.
    """
    __tablename__ = "Feedback"
    __table_args__ = {"schema": "gssp_common"}   # ✅ schema fixed

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Text, nullable=False)
    consumer_id = Column(Text, nullable=False)
    authorization_coin_id = Column(Text, nullable=False)
    feedback_json = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
