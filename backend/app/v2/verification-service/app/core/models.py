from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey
)
from .database import Base

class QrCodeRecord(Base):
    __tablename__ = "qr_code_records"

    qr_code_records_id = Column(Integer, primary_key=True, autoincrement=True)
    diplome_id = Column(Integer, nullable=False)
    etudiant_id = Column(String(10), nullable=False)
    qr_code_path = Column(String(255), nullable=False)
    identifiant_opaque = Column(String(255), nullable=False, unique=True)
    url_verification = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False)

# this service may also insert into historique_operations when a verification occurs
class HistoriqueOperation(Base):
    __tablename__ = "historique_operations"

    historique_operations_id = Column(Integer, primary_key=True, autoincrement=True)
    diplome_id = Column(Integer, nullable=False)
    type_operation = Column(String(50), nullable=False)
    ancien_hash = Column(String(64))
    nouvel_hash = Column(String(64), nullable=False)
    tx_id_fabric = Column(String(255), nullable=False)
    acteur_id = Column(Integer, nullable=False)
    ip_address = Column(String(45))
    ms_tenant_id = Column(String(255))
    commentaire = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, nullable=False)
