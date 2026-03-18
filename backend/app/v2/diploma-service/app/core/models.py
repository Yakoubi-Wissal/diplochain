from datetime import date, datetime
from sqlalchemy import Column, String, Date, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from core.database import Base

class EtudiantDiplome(Base):
    __tablename__ = "etudiant_diplome"
    
    id_diplome = Column(Integer, primary_key=True, autoincrement=True)
    etudiant_id = Column(String(20), nullable=False)
    session_diplome = Column(String(50), nullable=False)
    id_annexe = Column(Integer, nullable=False)
    num_diplome = Column(Integer, nullable=False)
    date_diplome = Column(Date, nullable=False)
    date_liv_diplome = Column(Date, nullable=False)

    blockchain_ext = relationship("DiplomeBlockchainExt", back_populates="diplome", uselist=False)

class DiplomeBlockchainExt(Base):
    __tablename__ = "diplome_blockchain_ext"

    id_diplome = Column(Integer, ForeignKey("etudiant_diplome.id_diplome"), primary_key=True)
    titre = Column(String(255))
    mention = Column(String(50))
    date_emission = Column(Date)
    annee_promotion = Column(String(20))
    hash_sha256 = Column(String(64), unique=True)
    tx_id_fabric = Column(String(255))
    ipfs_cid = Column(String(100))
    statut = Column(String, default="PENDING_BLOCKCHAIN")
    blockchain_retry_count = Column(Integer, default=0)
    blockchain_last_retry = Column(DateTime)
    generation_mode = Column(String(20), default="UPLOAD")
    template_id = Column(Integer)
    institution_id = Column(Integer)
    specialite_id = Column(String(3))
    uploaded_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    diplome = relationship("EtudiantDiplome", back_populates="blockchain_ext")

class HistoriqueOperations(Base):
    __tablename__ = "historique_operations"

    historique_operations_id = Column(Integer, primary_key=True, autoincrement=True)
    diplome_id = Column(Integer, ForeignKey("etudiant_diplome.id_diplome"), nullable=False)
    type_operation = Column(String, nullable=False)
    ancien_hash = Column(String(64))
    nouvel_hash = Column(String(64), nullable=False)
    tx_id_fabric = Column(String(255), nullable=False)
    acteur_id = Column(Integer, nullable=False)
    ip_address = Column(String(45))
    ms_tenant_id = Column(String(255))
    commentaire = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
