from sqlalchemy import Column, String, Integer, Text
from .database import Base

class Entreprise(Base):
    __tablename__ = "entreprise"

    id = Column(Integer, primary_key=True, index=True)
    nom_entreprise = Column(String(200), index=True)
    secteur_activite = Column(String(200))
    matricule_fiscale = Column(String(50), unique=True, index=True)
    email_contact = Column(String(100))
    telephone = Column(String(30))
    adresse = Column(Text)
    site_web = Column(String(255))
    id_user = Column(Integer)
