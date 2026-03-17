import uuid
from datetime import date

from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base

# models aligned with central diplochain_db schema (UUID primary keys)

class Diploma(Base):
    __tablename__ = "diplomes"  # note: french plural to match existing schema

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titre = Column(String(255), nullable=False)
    mention = Column(String(100), nullable=True)
    date_emission = Column(Date, nullable=False)
    hash_sha256 = Column(String(64), nullable=False)
    tx_id_fabric = Column(String(255), nullable=True)
    ipfs_cid = Column(String(255), nullable=False)
    statut = Column(String(50), nullable=False, server_default="ORIGINAL")
    etudiant_id = Column(UUID(as_uuid=True), nullable=False)
    institution_id = Column(UUID(as_uuid=True), nullable=False)
    specialite_id = Column(UUID(as_uuid=True), nullable=True)
    template_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(Date, nullable=False, server_default="now()")
    updated_at = Column(Date, nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)

class DiplomaStatusHistory(Base):
    __tablename__ = "diploma_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diploma_id = Column(UUID(as_uuid=True), ForeignKey("diplomes.id"), nullable=False)
    old_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    changed_at = Column(Date, nullable=False, default=date.today)
