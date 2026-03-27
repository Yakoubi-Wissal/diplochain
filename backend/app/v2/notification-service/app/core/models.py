from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from .database import Base

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type_notification = Column(String(50)) # e.g. "EMAIL", "SMS", "ALERT"
    message = Column(String(500))
    status = Column(String(20), default="PENDING") # "PENDING", "SENT", "FAILED"
    created_at = Column(DateTime, default=datetime.utcnow)
