from sqlalchemy import Column, Integer, String
from core.database import Base

class IPFSFile(Base):
    __tablename__ = "ipfs_files"
    file_id = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(String(255), unique=True)
    status = Column(String(50))

class PinningStatus(Base):
    __tablename__ = "pinning_status"
    pin_id = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(String(255))
    status = Column(String(50))
