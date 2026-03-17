from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric, ForeignKey, DateTime
)
from core.database import Base

class Rapport(Base):
    __tablename__ = "rapport"

    id_rapport = Column(Integer, primary_key=True, autoincrement=True)
    nom_documents = Column(String(255))
    id_langue = Column(Integer, nullable=False)
    id_type_impression = Column(Integer, nullable=False)
    id_annee = Column(Integer, nullable=False)
    etat = Column(Boolean)
    code_rapport = Column(String(25), unique=True)

class RapportInstitution(Base):
    __tablename__ = "rapport_institution"

    id_rapport = Column(Integer, ForeignKey("rapport.id_rapport"), primary_key=True)
    institution_id = Column(Integer, primary_key=True)
