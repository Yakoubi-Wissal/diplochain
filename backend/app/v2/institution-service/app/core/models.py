from sqlalchemy import (
    Column, Integer, String, Date, Numeric, Text, Boolean, DateTime,
    func
)
from core.database import Base


class Institution(Base):
    __tablename__ = "institution"

    institution_id = Column(Integer, primary_key=True, autoincrement=True)
    nom_institution = Column(String(255))
    adresse = Column(String(255))
    code_postal = Column(String(20))
    ville = Column(String(100))
    date_creation = Column(Date)
    pays = Column(String(100))
    telephone = Column(String(20))
    email_institution = Column(String(100))
    site_web = Column(String(255))
    chiffre_affaires = Column(Numeric(15,2))
    nombre_employes = Column(Integer)
    description = Column(String(255))
    id_group_institution = Column(Integer)
    date_mise_a_jour = Column(DateTime, default=func.now())

class InstitutionBlockchainExt(Base):
    __tablename__ = "institution_blockchain_ext"

    institution_id = Column(Integer, primary_key=True)
    channel_id = Column(String(100), unique=True)
    peer_node_url = Column(String(255))
    status = Column(String(50))
    code = Column(String(20))
    created_at = Column(DateTime, default=func.now())

# optional convenience entities
class SpecialiteExt(Base):
    __tablename__ = "specialite_ext"

    code_specialite = Column(String(3), primary_key=True)
    nom = Column(String(200))
    code = Column(String(20))
    institution_id = Column(Integer)
    is_active = Column(Boolean)
    created_at = Column(DateTime, default=func.now())

class TemplateDepartement(Base):
    __tablename__ = "template_departement"

    id = Column(String, primary_key=True)  # uuid stored as text
    nom = Column(String(255), nullable=False)
    departement_id = Column(String, nullable=False)
    institution_id = Column(Integer)
    fichier_jrxml_path = Column(String(500))
    fichier_jasper_path = Column(String(500))
    version = Column(Integer)
    is_active = Column(Boolean)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime)
