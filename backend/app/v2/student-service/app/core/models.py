from sqlalchemy import (
    Column, String, Date, Integer, Text, ForeignKey
)
from .database import Base

class Student(Base):
    __tablename__ = "etudiant"

    etudiant_id = Column(String(10), primary_key=True)
    email_etudiant = Column(String(100))
    nom = Column(String(100))
    prenom = Column(String(100))
    date_naissance = Column(Date)
    num_cin = Column(String(8))
    num_passeport = Column(String(20))
    entreprise_id = Column(Integer)
    telephone = Column(String(30))
    code_nationalite = Column(String(3))
    code_specialite = Column(String(3))
    date_delivrance = Column(Date)
    lieu_nais_et = Column(String(100))
    sexe = Column(String(1))
    lieu_delivrance = Column(String(100))
    id_user = Column(Integer)
    adresse_postale = Column(String(255))
    code_postal = Column(String(20))
    ville = Column(String(100))
    gouvernorat = Column(String(100))
    linkedin_id = Column(String(255))
    linkedin_url = Column(String(500))
    linkedin_data_id = Column(Integer)
    email_esprit_etudiant = Column(String(100))

# identifiers table no longer relevant; move to diploma-service or other
