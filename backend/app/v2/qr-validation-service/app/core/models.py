from sqlalchemy import Column, String, DateTime, JSON
from .database import Base
import datetime

class QRScanHistory(Base):
    __tablename__ = "qr_scan_history"
    id = Column(String, primary_key=True)
    scanned_at = Column(DateTime, default=datetime.datetime.utcnow)
    result = Column(JSON)
