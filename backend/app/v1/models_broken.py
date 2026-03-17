"""
models.py — DiploChain
Modèles SQLAlchemy alignés sur le schéma fusionné (schema_diplochain_fusionne.sql)

Légende :
  [O]     → Colonne/table conservée depuis l'original
  [V6]    → Colonne/table ajoutée depuis le fichier v6
  [FUSION]→ Table existant dans les deux — colonnes fusionnées
"""

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean, Column, Date, DateTime, ForeignKey, Integer,
    Numeric, String, Text, UniqueConstraint, text,

)
from sqlalchemy.dialects.postgresql import UUID, INET, ENUM
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from database import Base

# ─────────────────────────────────────────────────────────────────────────────
#  ENUMS PostgreSQL natifs
#  create_type=False car ils sont déjà créés par le SQL de migration.
#  Pour un environnement de test (Alembic), passer create_type=True.
# ─────────────────────────────────────────────────────────────────────────────

StatutInstitutionEnum = ENUM(
    "ACTIVE", "SUSPENDUE", "ARCHIVEE",
    name="statut_institution", create_type=False
)

StatutUserEnum = ENUM(
    "ACTIF", "EN_ATTENTE", "SUSPENDU",
    name="statut_user", create_type=False
)

StatutDiplomeEnum = ENUM(
    "PENDING_BLOCKCHAIN", "ORIGINAL", "MODIFIE", "DUPLIQUE", "REVOQUE",
    name="statut_diplome", create_type=False
)

TypeOperationEnum = ENUM(
    "CREATION", "MODIFICATION", "REVOCATION", "DUPLICATION", "VERIFICATION",
    name="type_operation", create_type=False
)

StatutValidationEnum = ENUM(
    "EN_ATTENTE", "APPROUVEE", "REFUSEE",
    name="statut_validation", create_type=False
)


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : nationalite [O]
# ─────────────────────────────────────────────────────────────────────────────
class Nationalite(Base):
    __tablename__ = "nationalite"

    code_nationalite        = Column(String(3),  primary_key=True)                # [O]
    designation_nationalite = Column(String(50), nullable=True)                   # [O]

    # Relations
    etudiants = relationship("Etudiant", back_populates="nationalite")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : institution [FUSION]
# ─────────────────────────────────────────────────────────────────────────────
class Institution(Base):
    __tablename__ = "institution"

    # [O] Colonnes originales
    institution_id       = Column(Integer,     primary_key=True)
    nom_institution      = Column(String(255), nullable=True)
    adresse              = Column(String(255), nullable=True)
    code_postal          = Column(String(20),  nullable=True)
    ville                = Column(String(100), nullable=True)
    date_creation        = Column(Date,        nullable=True)
    pays                 = Column(String(100), nullable=True)
    telephone            = Column(String(20),  nullable=True)
    email_institution    = Column(String(100), nullable=True)
    site_web             = Column(String(255), nullable=True)
    chiffre_affaires     = Column(Numeric(15, 2), nullable=True)
    nombre_employes      = Column(Integer,     nullable=True)
    description          = Column(String(255), nullable=True)
    id_group_institution = Column(Integer,     nullable=True)
    date_mise_a_jour     = Column(DateTime,    server_default=func.current_timestamp())

    # [V6] Colonnes ajoutées
    channel_id    = Column(String(100),      unique=True,  nullable=True)
    peer_node_url = Column(String(255),      nullable=True)
    statut        = Column(StatutInstitutionEnum, nullable=False, default="ACTIVE")
    code          = Column(String(20),       unique=True,  nullable=True)
    uuid_id       = Column(String(36), unique=True)  # UUID generated as string

    # Relations
    specialites     = relationship("Specialite",    back_populates="institution")
    utilisateurs    = relationship("User",          back_populates="institution", foreign_keys="User.institution_id")
    diplomes        = relationship("Diplome",        back_populates="institution")
    rapport_institutions = relationship("RapportInstitution", back_populates="institution")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : "ROLE" [FUSION]
# ─────────────────────────────────────────────────────────────────────────────
class Role(Base):
    __tablename__ = "ROLE"

    # [O] Colonnes originales
    id_role    = Column(Integer,     primary_key=True, autoincrement=True)
    label_role = Column(String(100), nullable=True)
    code       = Column(String(255), nullable=False, unique=True)
    id_cursus  = Column(Integer,     nullable=True)            # FK vers cursus (table externe)

    # [V6] Colonnes ajoutées
    description = Column(Text,       nullable=True)
    permissions = Column(JSON, nullable=True)
    is_active   = Column(Boolean,    nullable=False, default=True)
    created_at  = Column(DateTime,   nullable=False, server_default=func.now())
    uuid_id     = Column(String(36))

    # Relations
    utilisateurs = relationship("User", back_populates="role", foreign_keys="User.role_id")
    user_roles   = relationship("UserRole", back_populates="role")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : specialite [FUSION]
# ─────────────────────────────────────────────────────────────────────────────
class Specialite(Base):
    __tablename__ = "specialite"

    # [O] Colonnes originales
    code_specialite        = Column(String(3),  primary_key=True)
    designation_specialite = Column(String(50), nullable=True)

    # [V6] Colonnes ajoutées
    institution_id = Column(Integer, ForeignKey("institution.institution_id", ondelete="CASCADE"), nullable=True)
    is_active      = Column(Boolean,  nullable=False, default=True)
    created_at     = Column(DateTime, nullable=False, server_default=func.now())
    uuid_id        = Column(String(36))

    # Relations
    institution = relationship("Institution", back_populates="specialites")
    etudiants   = relationship("Etudiant",    back_populates="specialite")
    diplomes    = relationship("Diplome",     back_populates="specialite")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : entreprise [FUSION]
# ─────────────────────────────────────────────────────────────────────────────
class Entreprise(Base):
    __tablename__ = "entreprise"

    # [O] Colonnes originales
    id_entreprise     = Column(Integer,      primary_key=True, autoincrement=True)
    nom_entreprise    = Column(String(100),  nullable=False)
    raison_sociale    = Column(String(255),  nullable=True)
    matricule_fiscale = Column(String(15),   nullable=True, unique=True)
    secteur_activite  = Column(String(100),  nullable=True)
    adresse_siege     = Column(String(255),  nullable=True)
    code_postal       = Column(String(10),   nullable=True)
    ville             = Column(String(100),  nullable=True)
    pays              = Column(String(100),  nullable=True)
    telephone         = Column(String(20),   nullable=True)
    email_entreprise  = Column(String(100),  nullable=True)
    site_web          = Column(String(100),  nullable=True)
    date_creation     = Column(DateTime(timezone=True), nullable=True)
    capital_social    = Column(Numeric(15, 2), nullable=True)
    chiffre_affaires  = Column(Numeric(15, 2), nullable=True)
    nombre_employes   = Column(Integer,      nullable=True)
    status            = Column(Boolean,      nullable=False)           # [O] bool original
    date_mise_a_jour  = Column(DateTime,     server_default=func.current_timestamp())
    description       = Column(Text,         nullable=True)

    # [V6] Colonnes ajoutées
    siret                  = Column(String(20),  nullable=True)
    microsoft_tenant_id    = Column(String(255), unique=True, nullable=True)
    microsoft_email_domain = Column(String(255), nullable=True)
    statut                 = Column(StatutValidationEnum, nullable=False, default="EN_ATTENTE")
    invitation_token       = Column(String(500), nullable=True)
    token_expires_at       = Column(DateTime,    nullable=True)
    valide_par             = Column(Integer, ForeignKey("User.id_user", ondelete="SET NULL"), nullable=True)
    date_validation        = Column(DateTime,    nullable=True)
    uuid_id                = Column(String(36))

    # Relations
    validateur           = relationship("User", foreign_keys=[valide_par], back_populates="entreprises_validees")
    employes             = relationship("User", foreign_keys="User.entreprise_id", back_populates="entreprise")
    auth_sessions        = relationship("EntrepriseAuthSession", back_populates="entreprise")
    validation_requests  = relationship("EntrepriseValidationRequest", back_populates="entreprise")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : "User" [FUSION]
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "User"

    # [O] Colonnes originales
    id_user                     = Column(Integer,     primary_key=True, autoincrement=True)
    username                    = Column(String(255), nullable=True)
    password                    = Column(String(120), nullable=True)     # [O] SENSIBLE — conservé
    token                       = Column(String(255), nullable=True)
    tokentype                   = Column(String(50),  nullable=True)
    revoked                     = Column(Boolean,     default=False)
    expired                     = Column(Boolean,     default=False)
    email                       = Column(String(255), nullable=True)
    reset_code                  = Column(String(255), nullable=True)
    verificationtoken_expiration = Column(DateTime,   nullable=True)
    reset_code_expiration       = Column(DateTime,    nullable=True)
    verification_token          = Column(String(255), nullable=True, unique=True)
    status                      = Column(String(255), nullable=True)     # [O] varchar original

    # [V6] Colonnes ajoutées
    nom                    = Column(String(100), nullable=True)
    prenom                 = Column(String(100), nullable=True)
    role_id                = Column(Integer, ForeignKey("ROLE.id_role", ondelete="RESTRICT"), nullable=True)
    statut_diplochain      = Column(StatutUserEnum, nullable=False, default="EN_ATTENTE")
    last_login             = Column(DateTime,    nullable=True)
    niveau_acces           = Column(String(50),  default="GLOBAL")
    derniere_action_audit  = Column(DateTime,    nullable=True)
    institution_id         = Column(Integer,
                                    ForeignKey("institution.institution_id"), nullable=True)
    channel_session        = Column(String(255), nullable=True)
    permissions            = Column(JSON, nullable=True)
    blockchain_address     = Column(String(255), unique=True, nullable=True)
    numero_etudiant        = Column(String(50),  nullable=True)
    date_naissance_dc      = Column(Date,        nullable=True)
    promotion              = Column(String(100), nullable=True)
    entreprise_id          = Column(Integer,
                                    ForeignKey("entreprise.id_entreprise"), nullable=True)
    microsoft_email        = Column(String(255), nullable=True)
    ms_auth_validated_at   = Column(DateTime,    nullable=True)
    created_at             = Column(DateTime,    nullable=False, server_default=func.now())
    uuid_id                = Column(String(36))

    # Relations
    role         = relationship("Role", back_populates="utilisateurs", foreign_keys=[role_id])
    institution  = relationship("Institution", back_populates="utilisateurs", foreign_keys=[institution_id])
    entreprise   = relationship("Entreprise",  back_populates="employes", foreign_keys=[entreprise_id])
    user_roles   = relationship("UserRole",    back_populates="user")
    etudiant     = relationship("Etudiant",    back_populates="user", uselist=False)

    # Diplômes en tant qu'étudiant ou émetteur
    diplomes_etudiant  = relationship("Diplome", back_populates="etudiant", foreign_keys="Diplome.etudiant_id")
    diplomes_uploaded  = relationship("Diplome", back_populates="uploaded_by_user", foreign_keys="Diplome.uploaded_by")

    # Historique, sessions, validations
    historique_operations      = relationship("HistoriqueOperation", back_populates="acteur")
    auth_sessions              = relationship("EntrepriseAuthSession", back_populates="user")
    validation_requests_traite = relationship("EntrepriseValidationRequest", back_populates="traite_par_user", foreign_keys="EntrepriseValidationRequest.traite_par")
    entreprises_validees       = relationship("Entreprise", back_populates="validateur", foreign_keys="Entreprise.valide_par")
    qr_codes                   = relationship("QrCodeRecord", back_populates="etudiant_user")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : "UserRole" [O]
# ─────────────────────────────────────────────────────────────────────────────
class UserRole(Base):
    __tablename__ = "UserRole"

    user_id = Column(Integer, ForeignKey("User.id_user"),  primary_key=True)
    role_id = Column(Integer, ForeignKey("ROLE.id_role"),  primary_key=True)

    # Relations
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : etudiant [O]
# ─────────────────────────────────────────────────────────────────────────────
class Etudiant(Base):
    __tablename__ = "etudiant"

    etudiant_id           = Column(String(10),  primary_key=True)
    email_etudiant        = Column(String(100), nullable=True)
    nom                   = Column(String(100), nullable=True)
    date_naissance        = Column(Date,        nullable=True)
    num_cin               = Column(String(8),   nullable=True)
    num_passeport         = Column(String(20),  nullable=True)
    entreprise_id         = Column(Integer,     nullable=True)
    telephone             = Column(String(30),  nullable=True)
    code_nationalite      = Column(String(3),
                                   ForeignKey("nationalite.code_nationalite"), nullable=True)
    code_specialite       = Column(String(3),
                                   ForeignKey("specialite.code_specialite"), nullable=True)
    date_delivrance       = Column(Date,        nullable=True)
    lieu_nais_et          = Column(String(100), nullable=True)
    sexe                  = Column(String(1),   nullable=True)
    lieu_delivrance       = Column(String(100), nullable=True)
    prenom                = Column(String(100), nullable=True)
    id_user               = Column(Integer, ForeignKey("User.id_user", ondelete="SET NULL"), nullable=True, unique=True)
    adresse_postale       = Column(String(255), nullable=True)
    code_postal           = Column(String(20),  nullable=True)
    ville                 = Column(String(100), nullable=True)
    gouvernorat           = Column(String(100), nullable=True)
    linkedin_id           = Column(String(255), nullable=True)
    linkedin_url          = Column(String(500), nullable=True)
    linkedin_data_id      = Column(Integer,     nullable=True, unique=True)
    email_esprit_etudiant = Column(String(100), nullable=True)

    # Relations
    user         = relationship("User",        back_populates="etudiant")
    nationalite  = relationship("Nationalite", back_populates="etudiants")
    specialite   = relationship("Specialite",  back_populates="etudiants")
    diplomes_etudiant = relationship("EtudiantDiplome", back_populates="etudiant")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : etudiant_diplome [O]
# ─────────────────────────────────────────────────────────────────────────────
class EtudiantDiplome(Base):
    __tablename__ = "etudiant_diplome"

    id_diplome       = Column(Integer,     primary_key=True, autoincrement=True)
    etudiant_id      = Column(String(20), ForeignKey("etudiant.etudiant_id"), nullable=False)
    session_diplome  = Column(String(50),  nullable=False)
    id_annexe        = Column(Integer,     nullable=False)
    num_diplome      = Column(Integer,     nullable=False)
    date_diplome     = Column(Date,        nullable=False)
    date_liv_diplome = Column(Date,        nullable=False)

    # Relations
    etudiant = relationship("Etudiant", back_populates="diplomes_etudiant")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : rapport [O]
# ─────────────────────────────────────────────────────────────────────────────
class Rapport(Base):
    __tablename__ = "rapport"

    id_rapport         = Column(Integer,     primary_key=True)
    nom_documents      = Column(String(255), nullable=True)
    id_langue          = Column(Integer,     nullable=False)   # FK vers langue (table externe)
    id_type_impression = Column(Integer,     nullable=False)   # FK vers type_impression
    id_annee           = Column(Integer,     nullable=False)   # FK vers annee_universitaire
    etat               = Column(Boolean,     nullable=True)
    code_rapport       = Column(String(25),  unique=True, nullable=True)

    # Relations
    rapport_institutions = relationship("RapportInstitution", back_populates="rapport")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : rapport_institution [O]
# ─────────────────────────────────────────────────────────────────────────────
class RapportInstitution(Base):
    __tablename__ = "rapport_institution"

    id_rapport     = Column(Integer, ForeignKey("rapport.id_rapport"),      primary_key=True)
    institution_id = Column(Integer, ForeignKey("institution.institution_id"), primary_key=True)

    # Relations
    rapport     = relationship("Rapport",     back_populates="rapport_institutions")
    institution = relationship("Institution", back_populates="rapport_institutions")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : diplomes [V6] — Table centrale DiploChain
# ─────────────────────────────────────────────────────────────────────────────
class Diplome(Base):
    __tablename__ = "diplomes"

    id             = Column(String(36))
    titre          = Column(String(255),        nullable=False)
    mention        = Column(String(100),        nullable=True)

    # FKs adaptées aux PKs originales (int4)
    institution_id = Column(Integer,
                             ForeignKey("institution.institution_id", ondelete="RESTRICT"),    nullable=False)
    specialite_id  = Column(String(3),
                             ForeignKey("specialite.code_specialite", ondelete="SET NULL"),    nullable=True)
    etudiant_id    = Column(Integer,
                             ForeignKey("User.id_user", ondelete="RESTRICT"),    nullable=False)
    uploaded_by    = Column(Integer,
                             ForeignKey("User.id_user", ondelete="RESTRICT"),    nullable=False)

    # Ancres cryptographiques
    hash_sha256    = Column(String(64),         nullable=False)
    ipfs_cid       = Column(String(100),        nullable=False)

    # Hyperledger Fabric
    tx_id_fabric             = Column(String(255), nullable=True)
    statut                   = Column(StatutDiplomeEnum, nullable=False, default="PENDING_BLOCKCHAIN")
    blockchain_retry_count   = Column(Integer,   nullable=False, default=0)
    blockchain_last_retry    = Column(DateTime,  nullable=True)

    # Métadonnées
    date_emission   = Column(Date,        nullable=False, server_default=func.current_date())
    annee_promotion = Column(String(20),  nullable=True)
    generation_mode = Column(String(20),  nullable=False, default="UPLOAD")

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relations
    institution      = relationship("Institution",  back_populates="diplomes")
    specialite       = relationship("Specialite",   back_populates="diplomes")
    etudiant         = relationship("User",          back_populates="diplomes_etudiant", foreign_keys=[etudiant_id])
    uploaded_by_user = relationship("User",          back_populates="diplomes_uploaded", foreign_keys=[uploaded_by])
    qr_codes         = relationship("QrCodeRecord",       back_populates="diplome", cascade="all, delete-orphan")
    historique       = relationship("HistoriqueOperation", back_populates="diplome", cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : qr_code_records [V6]
# ─────────────────────────────────────────────────────────────────────────────
class QrCodeRecord(Base):
    __tablename__ = "qr_code_records"

    id                  = Column(String(36))
    diplome_id          = Column(String(36)), nullable=False)
    etudiant_id         = Column(Integer, ForeignKey("User.id_user", ondelete="CASCADE"), nullable=False)
    identifiant_opaque  = Column(String(255), nullable=False, unique=True)
    url_verification    = Column(String(500), nullable=False)
    qr_code_data        = Column(Text,        nullable=True)
    is_active           = Column(Boolean,     nullable=False, default=True)
    created_at          = Column(DateTime,    nullable=False, server_default=func.now())

    # Relations
    diplome       = relationship("Diplome", back_populates="qr_codes")
    etudiant_user = relationship("User",    back_populates="qr_codes", foreign_keys=[etudiant_id])


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : historique_operations [V6]
# ─────────────────────────────────────────────────────────────────────────────
class HistoriqueOperation(Base):
    __tablename__ = "historique_operations"

    id             = Column(String(36))
    diplome_id     = Column(String(36)), nullable=False)
    acteur_id      = Column(Integer, ForeignKey("User.id_user",  ondelete="RESTRICT"), nullable=False)
    type_operation = Column(TypeOperationEnum, nullable=False)
    ancien_hash    = Column(String(64),  nullable=True)
    nouvel_hash    = Column(String(64),  nullable=True)
    tx_id_fabric   = Column(String(255), nullable=True)
    commentaire    = Column(Text,        nullable=True)
    ip_address     = Column(INET,        nullable=True)
    timestamp      = Column(DateTime,    nullable=False, server_default=func.now())

    # Relations
    diplome = relationship("Diplome", back_populates="historique")
    acteur  = relationship("User",    back_populates="historique_operations")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : entreprise_auth_sessions [V6]
# ─────────────────────────────────────────────────────────────────────────────
class EntrepriseAuthSession(Base):
    __tablename__ = "entreprise_auth_sessions"

    session_id       = Column(String(36))
    entreprise_id    = Column(Integer,
                               ForeignKey("entreprise.id_entreprise", ondelete="CASCADE"), nullable=False)
    user_id          = Column(Integer,
                               ForeignKey("User.id_user", ondelete="CASCADE"), nullable=False)
    access_token_jwt = Column(Text,      nullable=False)
    refresh_token    = Column(Text,      nullable=True)
    issuer           = Column(String(500), nullable=True)
    audience         = Column(String(255), nullable=True)
    expires_at       = Column(DateTime,  nullable=False)
    is_valid         = Column(Boolean,   nullable=False, default=True)
    created_at       = Column(DateTime,  nullable=False, server_default=func.now())

    # Relations
    entreprise = relationship("Entreprise", back_populates="auth_sessions")
    user       = relationship("User",       back_populates="auth_sessions")


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : entreprise_validation_requests [V6]
# ─────────────────────────────────────────────────────────────────────────────
class EntrepriseValidationRequest(Base):
    __tablename__ = "entreprise_validation_requests"

    id            = Column(String(36))
    entreprise_id = Column(Integer,
                            ForeignKey("entreprise.id_entreprise", ondelete="CASCADE"), nullable=False)
    ms_tenant_id  = Column(String(255), nullable=False)
    ms_email      = Column(String(255), nullable=False)
    statut        = Column(StatutValidationEnum, nullable=False, default="EN_ATTENTE")
    demande_at    = Column(DateTime, nullable=False, server_default=func.now())
    traite_par    = Column(Integer, ForeignKey("User.id_user", ondelete="SET NULL"), nullable=True)
    traite_at     = Column(DateTime, nullable=True)
    motif_refus   = Column(Text,     nullable=True)

    # Relations
    entreprise       = relationship("Entreprise", back_populates="validation_requests")
    traite_par_user  = relationship("User",       back_populates="validation_requests_traite", foreign_keys=[traite_par])


# ─────────────────────────────────────────────────────────────────────────────
#  TABLE : dashboard_metrics_daily [V6]
# ─────────────────────────────────────────────────────────────────────────────
class DashboardMetricsDaily(Base):
    __tablename__ = "dashboard_metrics_daily"

    metric_date              = Column(Date,     primary_key=True)
    nb_diplomes_emis         = Column(Integer,  nullable=False, default=0)
    nb_diplomes_microservice = Column(Integer,  nullable=False, default=0)
    nb_diplomes_upload       = Column(Integer,  nullable=False, default=0)
    nb_nouveaux_etudiants    = Column(Integer,  nullable=False, default=0)
    nb_institutions_actives  = Column(Integer,  nullable=False, default=0)
    nb_diplomes_confirmes    = Column(Integer,  nullable=False, default=0)
    nb_diplomes_pending      = Column(Integer,  nullable=False, default=0)
    nb_diplomes_revoques     = Column(Integer,  nullable=False, default=0)
    nb_verifications         = Column(Integer,  nullable=False, default=0)
    updated_at               = Column(DateTime, nullable=False, server_default=func.now())