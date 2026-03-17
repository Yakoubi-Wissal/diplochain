"""
Minimal SQLAlchemy models for DiploChain - SQLite compatible
This version uses only standard SQLAlchemy types compatible with both SQLite and PostgreSQL
"""

import uuid
from datetime import date, datetime
from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON,
    Numeric, String, Text, UniqueConstraint, text, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# ── Enums ─────────────────────────────────────────────────────────────────────
class StatutInstitutionEnum(str):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class StatutUserEnum(str):
    EN_ATTENTE = "EN_ATTENTE"
    ACTIF = "ACTIF"
    SUSPENDU = "SUSPENDU"

class StatutDiplomeEnum(str):
    PENDING_BLOCKCHAIN = "PENDING_BLOCKCHAIN"
    ORIGINAL = "ORIGINAL"
    MODIFIE = "MODIFIE"
    DUPLIQUE = "DUPLIQUE"
    REVOQUE = "REVOQUE"

class TypeOperationEnum(str):
    CREATION = "CREATION"
    VERIFICATION = "VERIFICATION"
    REVOCATION = "REVOCATION"
    DUPLICATION = "DUPLICATION"

# ── Role Model ────────────────────────────────────────────────────────────────
class Role(Base):
    __tablename__ = "ROLE"
    
    id_role = Column(Integer, primary_key=True, autoincrement=True)
    label_role = Column(String(100), nullable=True)
    code = Column(String(255), nullable=False, unique=True)
    id_cursus = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    uuid_id = Column(String(36), unique=True)

# ── Institution Model ─────────────────────────────────────────────────────────
class Institution(Base):
    __tablename__ = "institution"
    
    institution_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ── Specialite Model ──────────────────────────────────────────────────────────
class Specialite(Base):
    __tablename__ = "specialite"
    
    specialite_id = Column(Integer, primary_key=True)
    label = Column(String(255), nullable=True)
    code = Column(String(100), unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ── Entreprise Model ──────────────────────────────────────────────────────────
class Entreprise(Base):
    __tablename__ = "entreprise"
    
    id_entreprise = Column(Integer, primary_key=True)
    raison_sociale = Column(String(255), nullable=True)
    secteur_activite = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ── User Model ────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "User"
    
    id_user = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(500), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    nom = Column(String(100), nullable=True)
    prenom = Column(String(100), nullable=True)
    role_id = Column(Integer, ForeignKey("ROLE.id_role"), nullable=True)
    statut_diplochain = Column(String(50), nullable=True)
    institution_id = Column(Integer, ForeignKey("institution.institution_id"), nullable=True)
    permissions = Column(JSON, nullable=True)
    blockchain_address = Column(String(255), unique=True, nullable=True)
    numero_etudiant = Column(String(50), nullable=True)
    promotion = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    uuid_id = Column(String(36), unique=True)
    
    role_obj = relationship("Role")
    institution = relationship("Institution")

# ── Diplome Model ─────────────────────────────────────────────────────────────
class Diplome(Base):
    __tablename__ = "diplomes"
    
    diplome_id = Column(Integer, primary_key=True)
    titre = Column(String(500), nullable=True)
    mention = Column(String(255), nullable=True)
    date_emission = Column(Date, nullable=True)
    hash_sha256 = Column(String(64), unique=True, nullable=True)
    tx_id_fabric = Column(String(255), nullable=True)
    ipfs_cid = Column(String(100), nullable=True)
    statut = Column(String(50), nullable=True)
    generation_mode = Column(String(50), nullable=True)
    blockchain_retry_count = Column(Integer, default=0)
    etudiant_id = Column(Integer, nullable=True)
    institution_id = Column(Integer, ForeignKey("institution.institution_id"), nullable=True)
    specialite_id = Column(Integer, ForeignKey("specialite.specialite_id"), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("User.id_user"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    institution = relationship("Institution")
    specialite = relationship("Specialite")

# ── QrCodeRecord Model ────────────────────────────────────────────────────────
class QrCodeRecord(Base):
    __tablename__ = "qr_code_record"
    
    qr_code_id = Column(Integer, primary_key=True)
    identifiant_opaque = Column(String(255), unique=True, nullable=True)
    diplome_id = Column(Integer, ForeignKey("diplomes.diplome_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ── HistoriqueOperation Model ─────────────────────────────────────────────────
class HistoriqueOperation(Base):
    __tablename__ = "historique_operations"
    
    historique_id = Column(Integer, primary_key=True)
    type_operation = Column(String(50), nullable=True)
    ancien_hash = Column(String(64), nullable=True)
    nouvel_hash = Column(String(64), nullable=True)
    tx_id_fabric = Column(String(255), nullable=True)
    acteur_id = Column(Integer, ForeignKey("User.id_user"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    commentaire = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
