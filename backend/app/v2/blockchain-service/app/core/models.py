from sqlalchemy import (
    Column, Integer, String, Date, Numeric, DateTime, func
)
from .database import Base

class DiplomaBlockchain(Base):
    __tablename__ = "diplome_blockchain_ext"

    id_diplome = Column(Integer, primary_key=True)
    titre = Column(String(255))
    mention = Column(String(50))
    date_emission = Column(Date)
    annee_promotion = Column(String(20))
    hash_sha256 = Column(String(64), unique=True)
    tx_id_fabric = Column(String(255))
    ipfs_cid = Column(String(100))
    statut = Column(String(50))
    blockchain_retry_count = Column(Integer, default=0)
    blockchain_last_retry = Column(DateTime)
    generation_mode = Column(String(20))
    template_id = Column(Integer)
    institution_id = Column(Integer)
    specialite_id = Column(String(3))
    uploaded_by = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
