"""
models.py — DiploChain Schema v6.0
Architecture Core (Esprit) + Extension (DiploChain)
"""

import uuid
from datetime import date, datetime
from enum import Enum
from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey, Integer,
    String, Text, func, Numeric, JSON, PrimaryKeyConstraint,
    ForeignKeyConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Enum as PgEnum


# ──────────────────────────────────────────────
# 1. Python Enums (Matching statut_* enums in SQL)
# ──────────────────────────────────────────────

class StatutDiplome(str, Enum):
    ORIGINAL = 'ORIGINAL'
    DUPLICATA = 'DUPLICATA'
    ANNULE = 'ANNULE'
    REVOQUE = 'REVOQUE'
    PENDING_BLOCKCHAIN = 'PENDING_BLOCKCHAIN'
    CONFIRME = 'CONFIRME'

class StatutInstitution(str, Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    SUSPENDED = 'SUSPENDED'

class StatutValidation(str, Enum):
    EN_ATTENTE = 'EN_ATTENTE'
    VALIDE = 'VALIDE'
    REFUSE = 'REFUSE'

class TypeOperation(str, Enum):
    EMISSION = 'EMISSION'
    REVOCATION = 'REVOCATION'
    VERIFICATION = 'VERIFICATION'
    MISE_A_JOUR = 'MISE_A_JOUR'

class StatutUserDiploChain(str, Enum):
    EN_ATTENTE = 'EN_ATTENTE'
    ACTIF = 'ACTIF'
    SUSPENDU = 'SUSPENDU'
    DESACTIVE = 'DESACTIVE'


# ──────────────────────────────────────────────
# 2. Base & PostgreSQL Enums
# ──────────────────────────────────────────────

class Base(DeclarativeBase):
    pass

statut_diplome_pg = PgEnum(StatutDiplome, name="statut_diplome", create_type=False)
statut_institution_pg = PgEnum(StatutInstitution, name="statut_institution", create_type=False)
statut_validation_pg = PgEnum(StatutValidation, name="statut_validation", create_type=False)
type_operation_pg = PgEnum(TypeOperation, name="type_operation", create_type=False)
statut_user_diplochain_pg = PgEnum(StatutUserDiploChain, name="statut_user_diplochain", create_type=False)


# ──────────────────────────────────────────────
# 3. SUPPORT / LOOKUP TABLES
# ──────────────────────────────────────────────

class AnneeUniversitaire(Base):
    __tablename__ = "annee_universitaire"
    id_annee = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String(50))

class Cursus(Base):
    __tablename__ = "cursus"
    id_cursus = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(255))
    roles = relationship("Role", back_populates="cursus")

class Langue(Base):
    __tablename__ = "langue"
    id_langue = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50))

class TypeImpression(Base):
    __tablename__ = "type_impression"
    id_type_impression = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50))

class TemplateDepartement(Base):
    __tablename__ = "template_departement"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False)
    departement_id = Column(UUID(as_uuid=True), nullable=False)
    institution_id = Column(Integer, ForeignKey("institution.institution_id"))
    fichier_jrxml_path = Column(String(500))
    fichier_jasper_path = Column(String(500))
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("User.id_user"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class LinkedinData(Base):
    __tablename__ = "linkedin_data"
    linkedin_data_id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(JSONB)
    etudiant = relationship("Etudiant", back_populates="linkedin_data")


# ──────────────────────────────────────────────
# 4. PROTECTED CORE TABLES (Esprit Central)
# ──────────────────────────────────────────────

class Role(Base):
    __tablename__ = "ROLE"
    id_role = Column(Integer, primary_key=True)
    label_role = Column(String(100))
    code = Column(String(255), nullable=False)
    id_cursus = Column(Integer, ForeignKey("cursus.id_cursus"))

    cursus = relationship("Cursus", back_populates="roles")
    ext = relationship("RoleExt", back_populates="core", uselist=False)
    user_roles = relationship("UserRole", back_populates="role")

class User(Base):
    __tablename__ = "User"
    id_user = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255))
    password = Column(String(120))
    token = Column(String(255))
    tokentype = Column(String(50))
    revoked = Column(Boolean, default=False)
    expired = Column(Boolean, default=False)
    email = Column(String(255))
    reset_code = Column(String(255))
    verificationtoken_expiration = Column(DateTime)
    reset_code_expiration = Column(DateTime)
    verification_token = Column(String(255), unique=True)
    status = Column(String(255)) # Must remain VARCHAR

    ext = relationship("UserExt", back_populates="core", uselist=False)
    user_roles = relationship("UserRole", back_populates="user")
    etudiant_profile = relationship("Etudiant", back_populates="user_core", uselist=False)

class UserRole(Base):
    __tablename__ = "UserRole"
    user_id = Column(Integer, ForeignKey("User.id_user"), primary_key=True)
    role_id = Column(Integer, ForeignKey("ROLE.id_role"), primary_key=True)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    ext = relationship("UserRoleExt", back_populates="core", uselist=False)

class Nationalite(Base):
    __tablename__ = "nationalite"
    code_nationalite = Column(String(3), primary_key=True)
    designation_nationalite = Column(String(50))

class Specialite(Base):
    __tablename__ = "specialite"
    code_specialite = Column(String(3), primary_key=True)
    designation_specialite = Column(String(50))
    
    ext = relationship("SpecialiteExt", back_populates="core", uselist=False)

class Institution(Base):
    __tablename__ = "institution"
    institution_id = Column(Integer, primary_key=True)
    nom_institution = Column(String(255))
    adresse = Column(String(255))
    code_postal = Column(String(20))
    ville = Column(String(100))
    date_creation = Column(Date)
    pays = Column(String(100))
    telephone = Column(String(20))
    email_institution = Column(String(100))
    site_web = Column(String(255))
    chiffre_affaires = Column(Numeric(15, 2))
    nombre_employes = Column(Integer)
    description = Column(String(255))
    id_group_institution = Column(Integer)
    date_mise_a_jour = Column(DateTime, server_default=func.now())

    blockchain_ext = relationship("InstitutionBlockchainExt", back_populates="core", uselist=False)

class Entreprise(Base):
    __tablename__ = "entreprise"
    id_entreprise = Column(Integer, primary_key=True, autoincrement=True)
    nom_entreprise = Column(String(100), nullable=False)
    raison_sociale = Column(String(255))
    matricule_fiscale = Column(String(15), unique=True)
    secteur_activite = Column(String(100))
    adresse_siege = Column(String(255))
    code_postal = Column(String(10))
    ville = Column(String(100))
    pays = Column(String(100))
    telephone = Column(String(20))
    email_entreprise = Column(String(100))
    site_web = Column(String(100))
    date_creation = Column(DateTime)
    capital_social = Column(Numeric(15, 2))
    chiffre_affaires = Column(Numeric(15, 2))
    nombre_employes = Column(Integer)
    status = Column(Boolean, nullable=False)
    date_mise_a_jour = Column(DateTime, server_default=func.now())
    description = Column(Text)

    ext = relationship("EntrepriseExt", back_populates="core", uselist=False)

class Etudiant(Base):
    __tablename__ = "etudiant"
    etudiant_id = Column(String(10), primary_key=True)
    email_etudiant = Column(String(100))
    nom = Column(String(100))
    date_naissance = Column(Date)
    num_cin = Column(String(8))
    num_passeport = Column(String(20))
    entreprise_id = Column(Integer)
    telephone = Column(String(30))
    code_nationalite = Column(String(3), ForeignKey("nationalite.code_nationalite"))
    code_specialite = Column(String(3), ForeignKey("specialite.code_specialite"))
    date_delivrance = Column(Date)
    lieu_nais_et = Column(String(100))
    sexe = Column(String(1))
    lieu_delivrance = Column(String(100))
    prenom = Column(String(100))
    id_user = Column(Integer, ForeignKey("User.id_user"), unique=True)
    adresse_postale = Column(String(255))
    code_postal = Column(String(20))
    ville = Column(String(100))
    gouvernorat = Column(String(100))
    linkedin_id = Column(String(255))
    linkedin_url = Column(String(500))
    linkedin_data_id = Column(Integer, ForeignKey("linkedin_data.linkedin_data_id"), unique=True)
    email_esprit_etudiant = Column(String(100))

    user_core = relationship("User", back_populates="etudiant_profile")
    linkedin_data = relationship("LinkedinData", back_populates="etudiant")
    diplomes = relationship("EtudiantDiplome", back_populates="etudiant")

class EtudiantDiplome(Base):
    __tablename__ = "etudiant_diplome"
    id_diplome = Column(Integer, primary_key=True, autoincrement=True)
    etudiant_id = Column(String(20), ForeignKey("etudiant.etudiant_id"), nullable=False)
    session_diplome = Column(String(50), nullable=False)
    id_annexe = Column(Integer, nullable=False)
    num_diplome = Column(Integer, nullable=False)
    date_diplome = Column(Date, nullable=False)
    date_liv_diplome = Column(Date, nullable=False)

    etudiant = relationship("Etudiant", back_populates="diplomes")
    blockchain_ext = relationship("DiplomeBlockchainExt", back_populates="core", uselist=False)

class Rapport(Base):
    __tablename__ = "rapport"
    id_rapport = Column(Integer, primary_key=True)
    nom_documents = Column(String(255))
    id_langue = Column(Integer, ForeignKey("langue.id_langue"), nullable=False)
    id_type_impression = Column(Integer, ForeignKey("type_impression.id_type_impression"), nullable=False)
    id_annee = Column(Integer, ForeignKey("annee_universitaire.id_annee"), nullable=False)
    etat = Column(Boolean)
    code_rapport = Column(String(25), unique=True)

class RapportInstitution(Base):
    __tablename__ = "rapport_institution"
    id_rapport = Column(Integer, ForeignKey("rapport.id_rapport"), primary_key=True)
    institution_id = Column(Integer, ForeignKey("institution.institution_id"), primary_key=True)


# ──────────────────────────────────────────────
# 5. DIPLOCHAIN EXTENSION TABLES
# ──────────────────────────────────────────────

class UserExt(Base):
    __tablename__ = "user_ext"
    user_id = Column(Integer, ForeignKey("User.id_user", ondelete="CASCADE"), primary_key=True)
    statut_diplochain = Column(statut_user_diplochain_pg, server_default='EN_ATTENTE')
    institution_id = Column(Integer, ForeignKey("institution.institution_id", ondelete="SET NULL"))
    niveau_acces = Column(String(50), default='GLOBAL')
    microsoft_email = Column(String(255))
    ms_auth_validated_at = Column(DateTime)
    channel_session = Column(String(255))
    blockchain_address = Column(String(255))
    permissions = Column(ARRAY(Text))
    numero_etudiant = Column(String(50))
    nom = Column(String(100))
    prenom = Column(String(100))
    date_naissance = Column(Date)
    promotion = Column(String(100))
    entreprise_id = Column(Integer, ForeignKey("entreprise.id_entreprise", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    derniere_action_audit = Column(DateTime)

    core = relationship("User", back_populates="ext")

class RoleExt(Base):
    __tablename__ = "role_ext"
    id_role = Column(Integer, ForeignKey("ROLE.id_role", ondelete="CASCADE"), primary_key=True)
    description = Column(Text)
    permissions = Column(ARRAY(Text))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    core = relationship("Role", back_populates="ext")

class UserRoleExt(Base):
    __tablename__ = "user_role_ext"
    user_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    description = Column(Text)
    permissions = Column(ARRAY(Text))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(['user_id', 'role_id'], ['UserRole.user_id', 'UserRole.role_id'], ondelete="CASCADE"),
    )
    core = relationship("UserRole", back_populates="ext")

# Custom fix: UserRole needs to be imported or referenced later if using strings
from sqlalchemy import ForeignKeyConstraint

class InstitutionBlockchainExt(Base):
    __tablename__ = "institution_blockchain_ext"
    institution_id = Column(Integer, ForeignKey("institution.institution_id", ondelete="CASCADE"), primary_key=True)
    channel_id = Column(String(100), unique=True)
    peer_node_url = Column(String(255))
    status = Column(statut_institution_pg, nullable=False, server_default='ACTIVE')
    code = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    core = relationship("Institution", back_populates="blockchain_ext")

class SpecialiteExt(Base):
    __tablename__ = "specialite_ext"
    code_specialite = Column(String(3), ForeignKey("specialite.code_specialite", ondelete="CASCADE"), primary_key=True)
    nom = Column(String(200))
    code = Column(String(20))
    institution_id = Column(Integer, ForeignKey("institution.institution_id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    core = relationship("Specialite", back_populates="ext")

class EntrepriseExt(Base):
    __tablename__ = "entreprise_ext"
    id_entreprise = Column(Integer, ForeignKey("entreprise.id_entreprise", ondelete="CASCADE"), primary_key=True)
    siret = Column(String(20))
    microsoft_tenant_id = Column(String(255))
    microsoft_email_domain = Column(String(255))
    statut_validation = Column(statut_validation_pg, server_default='EN_ATTENTE')
    invitation_token = Column(String(500))
    token_expires_at = Column(DateTime)
    valide_par = Column(Integer, ForeignKey("User.id_user", ondelete="SET NULL"))
    date_validation = Column(DateTime)

    core = relationship("Entreprise", back_populates="ext")

class DiplomeBlockchainExt(Base):
    __tablename__ = "diplome_blockchain_ext"
    id_diplome = Column(Integer, ForeignKey("etudiant_diplome.id_diplome", ondelete="CASCADE"), primary_key=True)
    titre = Column(String(255))
    mention = Column(String(50))
    date_emission = Column(Date)
    annee_promotion = Column(String(20))
    hash_sha256 = Column(String(64), unique=True)
    tx_id_fabric = Column(String(255))
    ipfs_cid = Column(String(100))
    statut = Column(statut_diplome_pg, server_default='PENDING_BLOCKCHAIN')
    blockchain_retry_count = Column(Integer, default=0)
    blockchain_last_retry = Column(DateTime)
    generation_mode = Column(String(20), default='UPLOAD')
    template_id = Column(Integer)
    institution_id = Column(Integer, ForeignKey("institution.institution_id", ondelete="SET NULL"))
    specialite_id = Column(String(3), ForeignKey("specialite.code_specialite", ondelete="SET NULL"))
    uploaded_by = Column(Integer, ForeignKey("User.id_user", ondelete="RESTRICT"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    core = relationship("EtudiantDiplome", back_populates="blockchain_ext")



# ──────────────────────────────────────────────
# 6. DIPLOCHAIN OPERATIONAL TABLES
# ──────────────────────────────────────────────

class HistoriqueOperation(Base):
    __tablename__ = "historique_operations"
    historique_operations_id = Column(Integer, primary_key=True, autoincrement=True)
    diplome_id = Column(Integer, ForeignKey("etudiant_diplome.id_diplome"), nullable=False)
    type_operation = Column(type_operation_pg, nullable=False)
    ancien_hash = Column(String(64))
    nouvel_hash = Column(String(64), nullable=False)
    tx_id_fabric = Column(String(255), nullable=False)
    acteur_id = Column(Integer, ForeignKey("User.id_user"), nullable=False)
    ip_address = Column(String(45))
    ms_tenant_id = Column(String(255))
    commentaire = Column(Text)
    user_agent = Column(Text)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())

class QrCodeRecord(Base):
    __tablename__ = "qr_code_records"
    qr_code_records_id = Column(Integer, primary_key=True, autoincrement=True)
    diplome_id = Column(Integer, ForeignKey("etudiant_diplome.id_diplome"), nullable=False)
    etudiant_id = Column(String(10), ForeignKey("etudiant.etudiant_id"), nullable=False)
    qr_code_path = Column(String(255), nullable=False)
    identifiant_opaque = Column(String(255), nullable=False, unique=True)
    url_verification = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

class EntrepriseAuthSession(Base):
    __tablename__ = "entreprise_auth_sessions"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    entreprise_id = Column(Integer, ForeignKey("entreprise.id_entreprise", ondelete="CASCADE"), nullable=False)
    access_token_jwt = Column(Text, nullable=False)
    tenant_id = Column(String(255), nullable=False)
    microsoft_email = Column(String(255), nullable=False)
    issuer = Column(String(500))
    audience = Column(String(255))
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

class EntrepriseValidationRequest(Base):
    __tablename__ = "entreprise_validation_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entreprise_id = Column(Integer, ForeignKey("entreprise.id_entreprise", ondelete="CASCADE"), nullable=False)
    ms_tenant_id = Column(String(255), nullable=False)
    ms_email = Column(String(255), nullable=False)
    statut = Column(statut_validation_pg, nullable=False, server_default='EN_ATTENTE')
    demande_at = Column(DateTime, nullable=False, server_default=func.now())
    traite_par = Column(Integer, ForeignKey("User.id_user", ondelete="SET NULL"))
    traite_at = Column(DateTime)
    motif_refus = Column(Text)

class DashboardMetricsDaily(Base):
    __tablename__ = "dashboard_metrics_daily"
    metric_date = Column(Date, primary_key=True)
    nb_diplomes_emis = Column(Integer, nullable=False, default=0)
    nb_diplomes_microservice = Column(Integer, nullable=False, default=0)
    nb_diplomes_upload = Column(Integer, nullable=False, default=0)
    nb_nouveaux_etudiants = Column(Integer, nullable=False, default=0)
    nb_institutions_actives = Column(Integer, nullable=False, default=0)
    nb_diplomes_confirmes = Column(Integer, nullable=False, default=0)
    nb_diplomes_pending = Column(Integer, nullable=False, default=0)
    nb_diplomes_revoques = Column(Integer, nullable=False, default=0)
    nb_verifications = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False, server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Text, nullable=False)
    operation = Column(String(10), nullable=False)
    changed_by = Column(Integer, ForeignKey("User.id_user", ondelete="SET NULL"))
    changed_at = Column(DateTime, nullable=False, server_default=func.now())
    old_values = Column(JSONB)
    new_values = Column(JSONB)
