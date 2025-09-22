# models.py

from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = {"schema": "gssp_common"}  # ✅ schema added

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(String, nullable=False)           # ✅ matches DB
    correlation_id = Column(String, nullable=False)
    content = Column(JSON, nullable=False)                     # ✅ JSON column
    soeid = Column(String, nullable=False)
    authorization_coin_id = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

db_feedback = models.Feedback(
    application_id=x_application_id,
    correlation_id=x_correlation_id,
    content=payload["content"],   # 👈 take "content" key from JSON
    soeid=x_soeid,
    authorization_coin_id=x_authorization_coin
)
