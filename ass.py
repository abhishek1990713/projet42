from sqlalchemy import Column, Integer, String, DateTime, JSON
from .database import Base

class Feedback(Base):
    __tablename__ = "idp_feedback"
    __table_args__ = {"schema": "gssp_common"}

    audit_id = Column(Integer, primary_key=True, index=True)
    consumer_coin = Column(String, nullable=True)
    app_id = Column(String, nullable=False)
    app_name = Column(String, nullable=True)
    usecase_config_id = Column(String, nullable=True)
    request = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    feedback = Column(JSON, nullable=False)  # renamed from feedback_json
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    correlation_id = Column(String, nullable=False)
