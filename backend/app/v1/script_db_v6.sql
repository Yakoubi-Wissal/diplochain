DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- STEP 0 ── DiploChain-specific ENUM types
-- These enums are ONLY used in extension tables, NEVER in core tables.
-- ─────────────────────────────────────────────────────────────────────────────

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statut_diplome') THEN
        CREATE TYPE statut_diplome AS ENUM (
            'ORIGINAL',
            'DUPLICATA',
            'ANNULE',
            'REVOQUE',
            'PENDING_BLOCKCHAIN',
            'CONFIRME'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statut_institution') THEN
        CREATE TYPE statut_institution AS ENUM (
            'ACTIVE',
            'INACTIVE',
            'SUSPENDED'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statut_validation') THEN
        CREATE TYPE statut_validation AS ENUM (
            'EN_ATTENTE',
            'VALIDE',
            'REFUSE'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'type_operation') THEN
        CREATE TYPE type_operation AS ENUM (
            'EMISSION',
            'REVOCATION',
            'VERIFICATION',
            'MISE_A_JOUR'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statut_user_diplochain') THEN
        CREATE TYPE statut_user_diplochain AS ENUM (
            'EN_ATTENTE',
            'ACTIF',
            'SUSPENDU',
            'DESACTIVE'
        );
    END IF;
END $$;


-- ─────────────────────────────────────────────────────────────────────────────
-- STEP 1 ── SUPPORT / LOOKUP TABLES
-- These are referenced by core tables via FK but were missing in script_db.sql.
-- ─────────────────────────────────────────────────────────────────────────────

-- Academic years (referenced by rapport)
CREATE TABLE IF NOT EXISTS public.annee_universitaire (
    id_annee   SERIAL  NOT NULL,
    label      VARCHAR(50),
    CONSTRAINT annee_universitaire_pkey PRIMARY KEY (id_annee)
);
COMMENT ON TABLE public.annee_universitaire IS 'Academic year reference table. Referenced by rapport.id_annee.';

-- Curriculum types (referenced by ROLE)
CREATE TABLE IF NOT EXISTS public.cursus (
    id_cursus  SERIAL  NOT NULL,
    nom        VARCHAR(255),
    CONSTRAINT cursus_pkey PRIMARY KEY (id_cursus)
);
COMMENT ON TABLE public.cursus IS 'Curriculum / programme types linked to ROLE.id_cursus.';

-- Report languages (referenced by rapport)
CREATE TABLE IF NOT EXISTS public.langue (
    id_langue  SERIAL  NOT NULL,
    nom        VARCHAR(50),
    CONSTRAINT langue_pkey PRIMARY KEY (id_langue)
);
COMMENT ON TABLE public.langue IS 'Language reference for report generation.';

-- Report print types (referenced by rapport)
CREATE TABLE IF NOT EXISTS public.type_impression (
    id_type_impression  SERIAL  NOT NULL,
    nom                 VARCHAR(50),
    CONSTRAINT type_impression_pkey PRIMARY KEY (id_type_impression)
);
COMMENT ON TABLE public.type_impression IS 'Print type reference for report generation.';

-- LinkedIn profile data (referenced by etudiant)
CREATE TABLE IF NOT EXISTS public.linkedin_data (
    linkedin_data_id  SERIAL  NOT NULL,
    data              JSONB,
    CONSTRAINT linkedin_data_pkey PRIMARY KEY (linkedin_data_id)
);
COMMENT ON TABLE public.linkedin_data IS 'Stores raw LinkedIn API JSON payload for a student profile.';


-- ─────────────────────────────────────────────────────────────────────────────
-- STEP 2 ── PROTECTED CORE TABLES (Esprit Central)
--
-- ⚠️  DO NOT MODIFY THESE TABLES IN ANY WAY:
--      • No column additions or removals
--      • No type changes
--      • No constraint changes
--      • No FK changes
--      • No primary key changes
-- ─────────────────────────────────────────────────────────────────────────────

-- ── 2.1 ROLE ─────────────────────────────────────────────────────────────────
-- Sequence must exist before the table that references it in its DEFAULT
CREATE SEQUENCE IF NOT EXISTS role_id_seq START 1;

CREATE TABLE public."ROLE" (
    id_role       INT DEFAULT nextval('role_id_seq'::regclass) NOT NULL,
    label_role    VARCHAR(100),
    code          VARCHAR(255) NOT NULL,
    id_cursus     INT,
    CONSTRAINT "ROLE_pkey"    PRIMARY KEY (id_role)
);
COMMENT ON TABLE public."ROLE" IS '[CORE — DO NOT MODIFY] Esprit role definitions.';

ALTER TABLE public."ROLE"
    ADD CONSTRAINT fk_role_cursus FOREIGN KEY (id_cursus)
    REFERENCES public.cursus(id_cursus);

-- ── 2.2 User ─────────────────────────────────────────────────────────────────
CREATE TABLE public."User" (
    id_user                       SERIAL4      NOT NULL,
    username                      VARCHAR(255),
    password                      VARCHAR(120),
    token                         VARCHAR(255),
    tokentype                     VARCHAR(50),
    revoked                       BOOL         DEFAULT false,
    expired                       BOOL         DEFAULT false,
    email                         VARCHAR(255),
    reset_code                    VARCHAR(255),
    verificationtoken_expiration  TIMESTAMP,
    reset_code_expiration         TIMESTAMP(6),
    verification_token            VARCHAR(255),
    status                        VARCHAR(255),     -- must remain varchar, never enum
    CONSTRAINT "User_pkey"                         PRIMARY KEY (id_user),
    CONSTRAINT ukjc62v1qe6cg3qydwxumad8725         UNIQUE (verification_token)
);
COMMENT ON TABLE public."User" IS '[CORE — DO NOT MODIFY] Esprit user accounts. status must remain VARCHAR(255).';

-- ── 2.3 UserRole ─────────────────────────────────────────────────────────────
CREATE TABLE public."UserRole" (
    user_id  INT4 NOT NULL,
    role_id  INT4 NOT NULL,
    CONSTRAINT "UserRole_pkey" PRIMARY KEY (user_id, role_id)
);
COMMENT ON TABLE public."UserRole" IS '[CORE — DO NOT MODIFY] Many-to-many user ↔ role join table.';

ALTER TABLE public."UserRole"
    ADD CONSTRAINT fk9isjsrduwxbciihv6c709c8y1 FOREIGN KEY (user_id)
    REFERENCES public."User"(id_user);
ALTER TABLE public."UserRole"
    ADD CONSTRAINT fkhg7xlakxx2f6qmf1glijyx7oq FOREIGN KEY (role_id)
    REFERENCES public."ROLE"(id_role);

-- ── 2.4 nationalite ──────────────────────────────────────────────────────────
CREATE TABLE public.nationalite (
    code_nationalite        VARCHAR(3)  NOT NULL,
    designation_nationalite VARCHAR(50),
    CONSTRAINT nationalite_pkey PRIMARY KEY (code_nationalite)
);
COMMENT ON TABLE public.nationalite IS '[CORE — DO NOT MODIFY] Nationality reference data.';

-- ── 2.5 specialite ───────────────────────────────────────────────────────────
CREATE TABLE public.specialite (
    code_specialite        VARCHAR(3)  NOT NULL,
    designation_specialite VARCHAR(50),
    CONSTRAINT specialite_pkey PRIMARY KEY (code_specialite)
);
COMMENT ON TABLE public.specialite IS '[CORE — DO NOT MODIFY] Academic speciality / major reference.';

-- ── 2.6 institution ──────────────────────────────────────────────────────────
CREATE TABLE public.institution (
    institution_id     INT4    NOT NULL,
    nom_institution    VARCHAR(255),
    adresse            VARCHAR(255),
    code_postal        VARCHAR(20),
    ville              VARCHAR(100),
    date_creation      DATE,
    pays               VARCHAR(100),
    telephone          VARCHAR(20),
    email_institution  VARCHAR(100),
    site_web           VARCHAR(255),
    chiffre_affaires   NUMERIC(15, 2),
    nombre_employes    INT4,
    description        VARCHAR(255),
    id_group_institution INT4,
    date_mise_a_jour   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT institution_pkey PRIMARY KEY (institution_id)
);
COMMENT ON TABLE public.institution IS '[CORE — DO NOT MODIFY] Issuing institutions. Blockchain fields go in institution_blockchain_ext.';

-- ── 2.7 entreprise ───────────────────────────────────────────────────────────
CREATE TABLE public.entreprise (
    id_entreprise      SERIAL4     NOT NULL,
    nom_entreprise     VARCHAR(100) NOT NULL,
    raison_sociale     VARCHAR(255),
    matricule_fiscale  VARCHAR(15),
    secteur_activite   VARCHAR(100),
    adresse_siege      VARCHAR(255),
    code_postal        VARCHAR(10),
    ville              VARCHAR(100),
    pays               VARCHAR(100),
    telephone          VARCHAR(20),
    email_entreprise   VARCHAR(100),
    site_web           VARCHAR(100),
    date_creation      TIMESTAMPTZ,
    capital_social     NUMERIC(15, 2),
    chiffre_affaires   NUMERIC(15, 2),
    nombre_employes    INT4,
    status             BOOL NOT NULL,
    date_mise_a_jour   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description        TEXT,
    CONSTRAINT entreprise_matricule_fiscale_key UNIQUE (matricule_fiscale),
    CONSTRAINT entreprise_pkey PRIMARY KEY (id_entreprise)
);
COMMENT ON TABLE public.entreprise IS '[CORE — DO NOT MODIFY] Employer companies. Microsoft/validation fields go in entreprise_ext.';

-- ── 2.8 etudiant ─────────────────────────────────────────────────────────────
CREATE TABLE public.etudiant (
    etudiant_id            VARCHAR(10) NOT NULL,
    email_etudiant         VARCHAR(100),
    nom                    VARCHAR(100),
    date_naissance         DATE,
    num_cin                VARCHAR(8),
    num_passeport          VARCHAR(20),
    entreprise_id          INT4,
    telephone              VARCHAR(30),
    code_nationalite       VARCHAR(3),
    code_specialite        VARCHAR(3),
    date_delivrance        DATE,
    lieu_nais_et           VARCHAR(100),
    sexe                   VARCHAR(1),
    lieu_delivrance        VARCHAR(100),
    prenom                 VARCHAR(100),
    id_user                INT4,
    adresse_postale        VARCHAR(255),
    code_postal            VARCHAR(20),
    ville                  VARCHAR(100),
    gouvernorat            VARCHAR(100),
    linkedin_id            VARCHAR(255),
    linkedin_url           VARCHAR(500),
    linkedin_data_id       INT4,
    email_esprit_etudiant  VARCHAR(100),
    CONSTRAINT etudiant_id_user_unique      UNIQUE (id_user),
    CONSTRAINT etudiant_linkedin_data_id_key UNIQUE (linkedin_data_id),
    CONSTRAINT etudiant_pkey                PRIMARY KEY (etudiant_id)
);
COMMENT ON TABLE public.etudiant IS '[CORE — DO NOT MODIFY] Student identity and contact information.';

ALTER TABLE public.etudiant
    ADD CONSTRAINT etudiant_id_user_fkey FOREIGN KEY (id_user)
    REFERENCES public."User"(id_user) ON DELETE SET NULL;
ALTER TABLE public.etudiant
    ADD CONSTRAINT fk76huvsu3jmhkj92d903gsfi8d FOREIGN KEY (code_specialite)
    REFERENCES public.specialite(code_specialite);
ALTER TABLE public.etudiant
    ADD CONSTRAINT fk_etudiant_linkedin FOREIGN KEY (linkedin_data_id)
    REFERENCES public.linkedin_data(linkedin_data_id) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE public.etudiant
    ADD CONSTRAINT fk_nationalite FOREIGN KEY (code_nationalite)
    REFERENCES public.nationalite(code_nationalite);

-- ── 2.9 etudiant_diplome ─────────────────────────────────────────────────────
-- CORE: only the 7 original columns. All blockchain data → diplome_blockchain_ext
CREATE TABLE public.etudiant_diplome (
    id_diplome       SERIAL4     NOT NULL,
    etudiant_id      VARCHAR(20) NOT NULL,
    session_diplome  VARCHAR(50) NOT NULL,
    id_annexe        INT4        NOT NULL,
    num_diplome      INT4        NOT NULL,
    date_diplome     DATE        NOT NULL,
    date_liv_diplome DATE        NOT NULL,
    CONSTRAINT etudiant_diplome_pkey PRIMARY KEY (id_diplome)
);
COMMENT ON TABLE public.etudiant_diplome IS '[CORE — DO NOT MODIFY] Core diploma record. Blockchain metadata goes in diplome_blockchain_ext.';

ALTER TABLE public.etudiant_diplome
    ADD CONSTRAINT fkbtfa92xk5l6wqw99nvi3tlvmi FOREIGN KEY (etudiant_id)
    REFERENCES public.etudiant(etudiant_id);

-- ── 2.10 rapport ─────────────────────────────────────────────────────────────
-- NOTE: script_db.sql defined this table twice (duplicate). Corrected: defined once.
CREATE TABLE public.rapport (
    id_rapport         INT4        NOT NULL,
    nom_documents      VARCHAR(255),
    id_langue          INT4        NOT NULL,
    id_type_impression INT4        NOT NULL,
    id_annee           INT4        NOT NULL,
    etat               BOOL,
    code_rapport       VARCHAR(25),
    CONSTRAINT rapport_pkey        PRIMARY KEY (id_rapport),
    CONSTRAINT unique_code_rapport UNIQUE (code_rapport)
);
COMMENT ON TABLE public.rapport IS '[CORE — DO NOT MODIFY] Report definitions. Duplicate removed from original script_db.sql.';

ALTER TABLE public.rapport
    ADD CONSTRAINT rapport_id_annee_fkey        FOREIGN KEY (id_annee)           REFERENCES public.annee_universitaire(id_annee);
ALTER TABLE public.rapport
    ADD CONSTRAINT rapport_id_langue_fkey        FOREIGN KEY (id_langue)          REFERENCES public.langue(id_langue);
ALTER TABLE public.rapport
    ADD CONSTRAINT rapport_id_type_impression_fkey FOREIGN KEY (id_type_impression) REFERENCES public.type_impression(id_type_impression);

-- ── 2.11 rapport_institution ─────────────────────────────────────────────────
CREATE TABLE public.rapport_institution (
    id_rapport     INT4 NOT NULL,
    institution_id INT4 NOT NULL,
    CONSTRAINT rapport_institution_pkey PRIMARY KEY (id_rapport, institution_id)
);
COMMENT ON TABLE public.rapport_institution IS '[CORE — DO NOT MODIFY] Many-to-many rapport ↔ institution.';

ALTER TABLE public.rapport_institution
    ADD CONSTRAINT rapport_institution_id_rapport_fkey    FOREIGN KEY (id_rapport)     REFERENCES public.rapport(id_rapport);
ALTER TABLE public.rapport_institution
    ADD CONSTRAINT rapport_institution_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institution(institution_id);


-- ─────────────────────────────────────────────────────────────────────────────
-- STEP 3 ── DIPLOCHAIN EXTENSION TABLES
-- These augment core tables without touching them.
-- Pattern: extension table PK = same as core table PK (1-to-0..1)
-- ─────────────────────────────────────────────────────────────────────────────

-- ── 3.1 user_ext — DiploChain profile extension for User ─────────────────────
CREATE TABLE public.user_ext (
    user_id                  INT4        NOT NULL,
    -- DiploChain-specific status (separate from core "User".status varchar)
    statut_diplochain        statut_user_diplochain DEFAULT 'EN_ATTENTE',
    -- Institutional access
    institution_id           INT4,
    niveau_acces             VARCHAR(50)  DEFAULT 'GLOBAL',
    -- Microsoft OAuth
    microsoft_email          VARCHAR(255),
    ms_auth_validated_at     TIMESTAMP,
    channel_session          VARCHAR(255),
    -- Blockchain
    blockchain_address       VARCHAR(255),
    permissions              TEXT[],
    -- Student reference
    numero_etudiant          VARCHAR(50),
    -- Profile (avoid duplicating etudiant.nom/prenom — use only for non-student users)
    nom                      VARCHAR(100),
    prenom                   VARCHAR(100),
    date_naissance           DATE,
    promotion                VARCHAR(100),
    -- Enterprise link
    entreprise_id            INT4,
    -- Audit
    created_at               TIMESTAMP    DEFAULT now(),
    last_login               TIMESTAMP,
    derniere_action_audit    TIMESTAMP,
    CONSTRAINT user_ext_pkey PRIMARY KEY (user_id)
);
COMMENT ON TABLE public.user_ext IS 'DiploChain extension for "User". All extra columns from backup that violated the core schema.';

ALTER TABLE public.user_ext
    ADD CONSTRAINT user_ext_user_id_fkey       FOREIGN KEY (user_id)       REFERENCES public."User"(id_user) ON DELETE CASCADE;
ALTER TABLE public.user_ext
    ADD CONSTRAINT user_ext_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institution(institution_id) ON DELETE SET NULL;
ALTER TABLE public.user_ext
    ADD CONSTRAINT user_ext_entreprise_id_fkey  FOREIGN KEY (entreprise_id) REFERENCES public.entreprise(id_entreprise) ON DELETE SET NULL;

CREATE INDEX idx_user_ext_blockchain_address ON public.user_ext(blockchain_address);
CREATE INDEX idx_user_ext_institution        ON public.user_ext(institution_id);
CREATE INDEX idx_user_ext_microsoft_email    ON public.user_ext(microsoft_email);

-- ── 3.2 role_ext — Extra metadata for ROLE ───────────────────────────────────
CREATE TABLE public.role_ext (
    id_role      INT4    NOT NULL,
    description  TEXT,
    permissions  TEXT[],
    is_active    BOOLEAN DEFAULT true,
    created_at   TIMESTAMP DEFAULT now(),
    CONSTRAINT role_ext_pkey PRIMARY KEY (id_role)
);
COMMENT ON TABLE public.role_ext IS 'DiploChain extension for "ROLE". Adds description, permissions, and lifecycle flags.';

ALTER TABLE public.role_ext
    ADD CONSTRAINT role_ext_id_role_fkey FOREIGN KEY (id_role) REFERENCES public."ROLE"(id_role) ON DELETE CASCADE;

-- ── 3.3 user_role_ext — Extra metadata for UserRole ──────────────────────────
CREATE TABLE public.user_role_ext (
    user_id      INT4    NOT NULL,
    role_id      INT4    NOT NULL,
    nom          VARCHAR(100),
    description  TEXT,
    permissions  TEXT[],
    is_active    BOOLEAN   DEFAULT true,
    created_at   TIMESTAMP DEFAULT now(),
    CONSTRAINT user_role_ext_pkey PRIMARY KEY (user_id, role_id)
);
COMMENT ON TABLE public.user_role_ext IS 'DiploChain extension for "UserRole". Adds name, permissions, and lifecycle flags.';

ALTER TABLE public.user_role_ext
    ADD CONSTRAINT user_role_ext_fk FOREIGN KEY (user_id, role_id) REFERENCES public."UserRole"(user_id, role_id) ON DELETE CASCADE;

-- ── 3.4 institution_blockchain_ext — Fabric channel data per institution ──────
CREATE TABLE public.institution_blockchain_ext (
    institution_id  INT4         NOT NULL,
    channel_id      VARCHAR(100),
    peer_node_url   VARCHAR(255),
    status          statut_institution NOT NULL DEFAULT 'ACTIVE',
    code            VARCHAR(20),
    created_at      TIMESTAMP DEFAULT now(),
    CONSTRAINT institution_blockchain_ext_pkey       PRIMARY KEY (institution_id),
    CONSTRAINT institution_blockchain_ext_channel_uq UNIQUE (channel_id)
);
COMMENT ON TABLE public.institution_blockchain_ext IS 'Hyperledger Fabric channel configuration per institution. Extends core institution table.';

ALTER TABLE public.institution_blockchain_ext
    ADD CONSTRAINT institution_blockchain_ext_inst_fk FOREIGN KEY (institution_id)
    REFERENCES public.institution(institution_id) ON DELETE CASCADE;

CREATE INDEX idx_inst_blockchain_channel ON public.institution_blockchain_ext(channel_id);

-- ── 3.5 specialite_ext — Institution assignment + lifecycle for specialite ────
CREATE TABLE public.specialite_ext (
    code_specialite  VARCHAR(3)  NOT NULL,
    nom              VARCHAR(200),
    code             VARCHAR(20),
    institution_id   INT4,
    is_active        BOOLEAN   DEFAULT true,
    created_at       TIMESTAMP DEFAULT now(),
    CONSTRAINT specialite_ext_pkey               PRIMARY KEY (code_specialite),
    -- A (code, institution_id) pair must be unique across the extension
    CONSTRAINT specialite_ext_code_inst_uq        UNIQUE (code, institution_id)
);
COMMENT ON TABLE public.specialite_ext IS 'DiploChain extension for specialite. Links programs to institutions and adds lifecycle management.';

ALTER TABLE public.specialite_ext
    ADD CONSTRAINT specialite_ext_code_fk        FOREIGN KEY (code_specialite)
    REFERENCES public.specialite(code_specialite) ON DELETE CASCADE;
ALTER TABLE public.specialite_ext
    ADD CONSTRAINT specialite_ext_institution_fk  FOREIGN KEY (institution_id)
    REFERENCES public.institution(institution_id) ON DELETE SET NULL;

CREATE INDEX idx_specialite_ext_institution ON public.specialite_ext(institution_id);

-- ── 3.6 entreprise_ext — Microsoft OAuth + validation data for entreprise ─────
CREATE TABLE public.entreprise_ext (
    id_entreprise         INT4    NOT NULL,
    siret                 VARCHAR(20),
    microsoft_tenant_id   VARCHAR(255),
    microsoft_email_domain VARCHAR(255),
    statut_validation     statut_validation DEFAULT 'EN_ATTENTE',
    invitation_token      VARCHAR(500),
    token_expires_at      TIMESTAMP,
    valide_par            INT4,             -- User who validated the company
    date_validation       TIMESTAMP,
    CONSTRAINT entreprise_ext_pkey PRIMARY KEY (id_entreprise)
);
COMMENT ON TABLE public.entreprise_ext IS 'Microsoft OAuth + validation workflow extension for entreprise. Avoids modifying the core table.';

ALTER TABLE public.entreprise_ext
    ADD CONSTRAINT entreprise_ext_id_fk        FOREIGN KEY (id_entreprise) REFERENCES public.entreprise(id_entreprise) ON DELETE CASCADE;
ALTER TABLE public.entreprise_ext
    ADD CONSTRAINT entreprise_ext_valide_par_fk FOREIGN KEY (valide_par)   REFERENCES public."User"(id_user) ON DELETE SET NULL;

CREATE INDEX idx_entreprise_ext_tenant      ON public.entreprise_ext(microsoft_tenant_id);
CREATE INDEX idx_entreprise_ext_statut      ON public.entreprise_ext(statut_validation);
CREATE INDEX idx_entreprise_ext_invite_tok  ON public.entreprise_ext(invitation_token);

-- ── 3.7 diplome_blockchain_ext — Blockchain metadata for etudiant_diplome ─────
-- This is the most critical extension table.
-- The backup had injected 16 columns directly into etudiant_diplome (core table).
-- All those columns live here instead.
CREATE TABLE public.diplome_blockchain_ext (
    id_diplome              INT4         NOT NULL,
    -- Document metadata
    titre                   VARCHAR(255),
    mention                 VARCHAR(50),
    date_emission           DATE,
    annee_promotion         VARCHAR(20),
    -- Blockchain anchoring
    hash_sha256             CHAR(64),              -- SHA-256 of the diploma document
    tx_id_fabric            VARCHAR(255),           -- Hyperledger Fabric transaction ID
    ipfs_cid                VARCHAR(100),           -- IPFS content identifier
    statut                  statut_diplome DEFAULT 'ORIGINAL',
    blockchain_retry_count  INT4          DEFAULT 0,
    blockchain_last_retry   TIMESTAMP,
    -- Generation
    generation_mode         VARCHAR(20)   DEFAULT 'UPLOAD',  -- UPLOAD | MICROSERVICE
    template_id             INT4,
    -- Relations
    institution_id          INT4,
    specialite_id           VARCHAR(3),
    uploaded_by             INT4,
    -- Timestamps
    created_at              TIMESTAMP DEFAULT now(),
    updated_at              TIMESTAMP,
    CONSTRAINT diplome_blockchain_ext_pkey     PRIMARY KEY (id_diplome),
    CONSTRAINT diplome_blockchain_ext_hash_uq  UNIQUE (hash_sha256)  -- each document has a unique fingerprint
);
COMMENT ON TABLE public.diplome_blockchain_ext IS
    'Blockchain metadata extension for etudiant_diplome. '
    'Contains hash_sha256, Fabric tx_id, IPFS CID, statut, and all DiploChain-specific fields. '
    'The UNIQUE constraint on hash_sha256 prevents duplicate diploma registration on-chain.';

ALTER TABLE public.diplome_blockchain_ext
    ADD CONSTRAINT dbe_diplome_fk      FOREIGN KEY (id_diplome)   REFERENCES public.etudiant_diplome(id_diplome) ON DELETE CASCADE;
ALTER TABLE public.diplome_blockchain_ext
    ADD CONSTRAINT dbe_institution_fk  FOREIGN KEY (institution_id) REFERENCES public.institution(institution_id) ON DELETE SET NULL;
ALTER TABLE public.diplome_blockchain_ext
    ADD CONSTRAINT dbe_specialite_fk   FOREIGN KEY (specialite_id)  REFERENCES public.specialite(code_specialite) ON DELETE SET NULL;
ALTER TABLE public.diplome_blockchain_ext
    ADD CONSTRAINT dbe_uploaded_by_fk  FOREIGN KEY (uploaded_by)    REFERENCES public."User"(id_user) ON DELETE RESTRICT;

-- Critical indexes for blockchain lookups
CREATE INDEX idx_dbe_hash        ON public.diplome_blockchain_ext(hash_sha256);
CREATE INDEX idx_dbe_tx_id       ON public.diplome_blockchain_ext(tx_id_fabric);
CREATE INDEX idx_dbe_statut      ON public.diplome_blockchain_ext(statut);
CREATE INDEX idx_dbe_institution ON public.diplome_blockchain_ext(institution_id);
CREATE INDEX idx_dbe_uploaded_by ON public.diplome_blockchain_ext(uploaded_by);
CREATE INDEX idx_dbe_created_at  ON public.diplome_blockchain_ext(created_at);


-- ─────────────────────────────────────────────────────────────────────────────
-- STEP 4 ── DIPLOCHAIN OPERATIONAL TABLES
-- New tables from the backup that are valid and correctly structured.
-- ─────────────────────────────────────────────────────────────────────────────

-- ── 4.1 historique_operations — Immutable blockchain audit log ────────────────
CREATE TABLE public.historique_operations (
    historique_operations_id  SERIAL      NOT NULL,
    diplome_id                INT4        NOT NULL,
    type_operation            type_operation NOT NULL,
    ancien_hash               CHAR(64),              -- previous SHA-256 (for updates)
    nouvel_hash               CHAR(64)    NOT NULL,  -- new SHA-256
    tx_id_fabric              VARCHAR(255) NOT NULL,
    acteur_id                 INT4        NOT NULL,  -- User who performed the operation
    ip_address                VARCHAR(45),
    ms_tenant_id              VARCHAR(255),
    commentaire               TEXT,
    user_agent                TEXT,
    "timestamp"               TIMESTAMP   NOT NULL DEFAULT now(),
    CONSTRAINT historique_operations_pkey PRIMARY KEY (historique_operations_id)
);
COMMENT ON TABLE public.historique_operations IS
    'Immutable blockchain audit trail. Records every EMISSION, REVOCATION, VERIFICATION, MISE_A_JOUR. '
    'RLS is enabled to restrict visibility by institution.';

-- Enable Row-Level Security (preserved from backup)
ALTER TABLE public.historique_operations ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.historique_operations
    ADD CONSTRAINT historique_ops_diplome_fk FOREIGN KEY (diplome_id)
    REFERENCES public.etudiant_diplome(id_diplome);
ALTER TABLE public.historique_operations
    ADD CONSTRAINT historique_ops_acteur_fk  FOREIGN KEY (acteur_id)
    REFERENCES public."User"(id_user);

CREATE INDEX idx_historique_diplome   ON public.historique_operations(diplome_id);
CREATE INDEX idx_historique_acteur    ON public.historique_operations(acteur_id);
CREATE INDEX idx_historique_timestamp ON public.historique_operations("timestamp");
CREATE INDEX idx_historique_type      ON public.historique_operations(type_operation);

-- ── 4.2 qr_code_records — QR verification tokens ─────────────────────────────
CREATE TABLE public.qr_code_records (
    qr_code_records_id   SERIAL       NOT NULL,
    diplome_id           INT4         NOT NULL,
    etudiant_id          VARCHAR(10)  NOT NULL,
    qr_code_path         VARCHAR(255) NOT NULL,
    identifiant_opaque   VARCHAR(255) NOT NULL,  -- opaque token for public verification URL
    url_verification     VARCHAR(500) NOT NULL,
    created_at           TIMESTAMP    NOT NULL DEFAULT now(),
    CONSTRAINT qr_code_records_pkey                   PRIMARY KEY (qr_code_records_id),
    CONSTRAINT qr_code_records_identifiant_opaque_key UNIQUE (identifiant_opaque)
);
COMMENT ON TABLE public.qr_code_records IS
    'QR code tokens linking to the public diploma verification endpoint. '
    'identifiant_opaque is the URL-safe token; url_verification is the full public URL.';

ALTER TABLE public.qr_code_records
    ADD CONSTRAINT qr_diplome_fk   FOREIGN KEY (diplome_id)  REFERENCES public.etudiant_diplome(id_diplome);
ALTER TABLE public.qr_code_records
    ADD CONSTRAINT qr_etudiant_fk  FOREIGN KEY (etudiant_id) REFERENCES public.etudiant(etudiant_id);

CREATE INDEX idx_qr_diplome    ON public.qr_code_records(diplome_id);
CREATE INDEX idx_qr_etudiant   ON public.qr_code_records(etudiant_id);

-- ── 4.3 entreprise_auth_sessions — Microsoft OAuth session store ──────────────
CREATE TABLE public.entreprise_auth_sessions (
    session_id        SERIAL       NOT NULL,
    entreprise_id     INT4         NOT NULL,
    access_token_jwt  TEXT         NOT NULL,
    tenant_id         VARCHAR(255) NOT NULL,
    microsoft_email   VARCHAR(255) NOT NULL,
    issuer            VARCHAR(500),
    audience          VARCHAR(255),
    expires_at        TIMESTAMP    NOT NULL,
    is_valid          BOOLEAN      NOT NULL DEFAULT true,
    created_at        TIMESTAMP    NOT NULL DEFAULT now(),
    CONSTRAINT entreprise_auth_sessions_pkey PRIMARY KEY (session_id)
);
COMMENT ON TABLE public.entreprise_auth_sessions IS
    'Stores active Microsoft OAuth JWT sessions for enterprise users. '
    'Sessions are invalidated by setting is_valid = false on logout or expiry.';

ALTER TABLE public.entreprise_auth_sessions
    ADD CONSTRAINT eas_entreprise_fk FOREIGN KEY (entreprise_id)
    REFERENCES public.entreprise(id_entreprise) ON DELETE CASCADE;

CREATE INDEX idx_eas_entreprise  ON public.entreprise_auth_sessions(entreprise_id);
CREATE INDEX idx_eas_is_valid    ON public.entreprise_auth_sessions(is_valid);
CREATE INDEX idx_eas_expires_at  ON public.entreprise_auth_sessions(expires_at);

-- ── 4.4 entreprise_validation_requests — Admin approval workflow ──────────────
CREATE TABLE public.entreprise_validation_requests (
    id             SERIAL       NOT NULL,
    entreprise_id  INT4         NOT NULL,
    ms_tenant_id   VARCHAR(255) NOT NULL,
    ms_email       VARCHAR(255) NOT NULL,
    statut         statut_validation NOT NULL DEFAULT 'EN_ATTENTE',
    demande_at     TIMESTAMP    NOT NULL DEFAULT now(),
    traite_par     INT4,        -- admin user who processed the request
    traite_at      TIMESTAMP,
    motif_refus    TEXT,        -- rejection reason
    CONSTRAINT entreprise_validation_requests_pkey PRIMARY KEY (id)
);
COMMENT ON TABLE public.entreprise_validation_requests IS
    'Admin approval workflow for new enterprise registrations. '
    'Each request goes through EN_ATTENTE → VALIDE or REFUSE.';

ALTER TABLE public.entreprise_validation_requests
    ADD CONSTRAINT evr_entreprise_fk  FOREIGN KEY (entreprise_id) REFERENCES public.entreprise(id_entreprise) ON DELETE CASCADE;
ALTER TABLE public.entreprise_validation_requests
    ADD CONSTRAINT evr_traite_par_fk  FOREIGN KEY (traite_par)    REFERENCES public."User"(id_user) ON DELETE SET NULL;

CREATE INDEX idx_evr_entreprise ON public.entreprise_validation_requests(entreprise_id);
CREATE INDEX idx_evr_statut     ON public.entreprise_validation_requests(statut);

-- ── 4.5 dashboard_metrics_daily — Aggregated KPI table ───────────────────────
CREATE TABLE public.dashboard_metrics_daily (
    metric_date              DATE    NOT NULL,
    nb_diplomes_emis         INT4    NOT NULL DEFAULT 0,
    nb_diplomes_microservice INT4    NOT NULL DEFAULT 0,
    nb_diplomes_upload       INT4    NOT NULL DEFAULT 0,
    nb_nouveaux_etudiants    INT4    NOT NULL DEFAULT 0,
    nb_institutions_actives  INT4    NOT NULL DEFAULT 0,
    nb_diplomes_confirmes    INT4    NOT NULL DEFAULT 0,
    nb_diplomes_pending      INT4    NOT NULL DEFAULT 0,
    nb_diplomes_revoques     INT4    NOT NULL DEFAULT 0,
    nb_verifications         INT4    NOT NULL DEFAULT 0,
    updated_at               TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT dashboard_metrics_daily_pkey PRIMARY KEY (metric_date)
);
COMMENT ON TABLE public.dashboard_metrics_daily IS
    'Daily aggregated KPIs for the DiploChain admin dashboard. '
    'Populated by a scheduled job — do not write directly from application code.';

CREATE INDEX idx_dashboard_metric_date ON public.dashboard_metrics_daily(metric_date DESC);


-- ─────────────────────────────────────────────────────────────────────────────
-- STEP 5 ── AUDIT LOG TABLE (new — proposed improvement)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE public.audit_log (
    audit_id    BIGSERIAL   NOT NULL,
    table_name  VARCHAR(100) NOT NULL,
    record_id   TEXT         NOT NULL,
    operation   VARCHAR(10)  NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
    changed_by  INT4,
    changed_at  TIMESTAMP    NOT NULL DEFAULT now(),
    old_values  JSONB,
    new_values  JSONB,
    CONSTRAINT audit_log_pkey PRIMARY KEY (audit_id)
);
COMMENT ON TABLE public.audit_log IS
    'Generic audit log for critical table changes. '
    'Populated via PostgreSQL trigger functions on sensitive tables.';

ALTER TABLE public.audit_log
    ADD CONSTRAINT audit_log_changed_by_fk FOREIGN KEY (changed_by)
    REFERENCES public."User"(id_user) ON DELETE SET NULL;

CREATE INDEX idx_audit_table_name ON public.audit_log(table_name);
CREATE INDEX idx_audit_changed_at ON public.audit_log(changed_at DESC);
CREATE INDEX idx_audit_changed_by ON public.audit_log(changed_by);


-- =============================================================================
-- STEP 7 ── v6 OBJECTS : Vues Dashboard, Fonction métriques, Index additionnels
-- =============================================================================

-- ── 7.1 Contrainte métier : tx_id_fabric obligatoire dès statut ≠ PENDING ────
-- Ajoutée sur diplome_blockchain_ext pour garantir l'intégrité blockchain.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_tx_id_required_when_confirmed'
    ) THEN
        ALTER TABLE public.diplome_blockchain_ext
            ADD CONSTRAINT chk_tx_id_required_when_confirmed
            CHECK (
                statut = 'PENDING_BLOCKCHAIN'
                OR (statut <> 'PENDING_BLOCKCHAIN' AND tx_id_fabric IS NOT NULL)
            );
        RAISE NOTICE 'Contrainte chk_tx_id_required_when_confirmed ajoutée';
    END IF;
END
$$;
COMMENT ON CONSTRAINT chk_tx_id_required_when_confirmed ON public.diplome_blockchain_ext IS
    'v6 — tx_id_fabric est obligatoire pour tout statut autre que PENDING_BLOCKCHAIN.';

-- ── 7.2 Index additionnels v6 (Dashboard Super Admin) ─────────────────────────

-- Requêtes Dashboard triées par date d'émission décroissante
CREATE INDEX IF NOT EXISTS idx_diplomes_date_emission_desc
    ON public.diplome_blockchain_ext(date_emission DESC);
COMMENT ON INDEX idx_diplomes_date_emission_desc IS
    'v6 Dashboard — tris par date d''émission décroissante O(log n).';

-- Filtre analytics UPLOAD vs MICROSERVICE
CREATE INDEX IF NOT EXISTS idx_diplomes_generation
    ON public.diplome_blockchain_ext(generation_mode);
COMMENT ON INDEX idx_diplomes_generation IS
    'v6 Dashboard — filtrage mode génération (UPLOAD | MICROSERVICE).';

-- Index partiel : Retry Worker scanne uniquement les PENDING_BLOCKCHAIN
CREATE INDEX IF NOT EXISTS idx_diplomes_pending
    ON public.diplome_blockchain_ext(id_diplome)
    WHERE statut = 'PENDING_BLOCKCHAIN';
COMMENT ON INDEX idx_diplomes_pending IS
    'v6 Retry Worker — index partiel sur PENDING_BLOCKCHAIN uniquement.';

-- Métriques nouveaux étudiants par jour (jointure via user_ext)
CREATE INDEX IF NOT EXISTS idx_etudiants_created_at
    ON public.user_ext(created_at);
COMMENT ON INDEX idx_etudiants_created_at IS
    'v6 Dashboard — métriques nb_nouveaux_etudiants par jour.';

-- ── 7.3 Vue v_diplomas_per_student — Dashboard Super Admin ────────────────────
-- Calcule en temps réel le nombre et statut des diplômes par étudiant.
CREATE OR REPLACE VIEW public.v_diplomas_per_student AS
SELECT
    e.etudiant_id,
    e.nom,
    e.prenom,
    e.email_etudiant                                          AS email,
    ue.numero_etudiant,
    COUNT(ed.id_diplome)                                      AS nb_diplomes_total,
    COUNT(CASE WHEN dbe.statut = 'ORIGINAL'       THEN 1 END) AS nb_confirmes,
    COUNT(CASE WHEN dbe.statut = 'PENDING_BLOCKCHAIN' THEN 1 END) AS nb_pending,
    COUNT(CASE WHEN dbe.statut = 'REVOQUE'         THEN 1 END) AS nb_revoques,
    MAX(dbe.date_emission)                                    AS derniere_emission
FROM public.etudiant e
LEFT JOIN public.user_ext ue           ON ue.user_id = e.id_user
LEFT JOIN public.etudiant_diplome ed   ON ed.etudiant_id = e.etudiant_id
LEFT JOIN public.diplome_blockchain_ext dbe ON dbe.id_diplome = ed.id_diplome
GROUP BY e.etudiant_id, e.nom, e.prenom, e.email_etudiant, ue.numero_etudiant
ORDER BY nb_diplomes_total DESC;

COMMENT ON VIEW public.v_diplomas_per_student IS
    'v6 Dashboard — vue temps réel des diplômes par étudiant. Utilisée par GET /api/admin/students.';

-- ── 7.4 Vue v_diplomas_per_institution — Dashboard Super Admin ────────────────
-- Agrège par institution le volume et mode de génération des diplômes.
CREATE OR REPLACE VIEW public.v_diplomas_per_institution AS
SELECT
    i.institution_id,
    i.nom_institution                                               AS nom,
    ibc.code,
    ibc.status                                                      AS statut,
    COUNT(dbe.id_diplome)                                           AS nb_diplomes_total,
    COUNT(CASE WHEN dbe.generation_mode = 'MICROSERVICE' THEN 1 END) AS nb_via_microservice,
    COUNT(CASE WHEN dbe.generation_mode = 'UPLOAD'       THEN 1 END) AS nb_via_upload,
    COUNT(CASE WHEN dbe.statut = 'PENDING_BLOCKCHAIN'    THEN 1 END) AS nb_pending,
    COUNT(CASE WHEN dbe.statut = 'REVOQUE'               THEN 1 END) AS nb_revoques,
    MAX(dbe.date_emission)                                          AS derniere_emission
FROM public.institution i
LEFT JOIN public.institution_blockchain_ext ibc ON ibc.institution_id = i.institution_id
LEFT JOIN public.diplome_blockchain_ext dbe     ON dbe.institution_id  = i.institution_id
GROUP BY i.institution_id, i.nom_institution, ibc.code, ibc.status
ORDER BY nb_diplomes_total DESC;

COMMENT ON VIEW public.v_diplomas_per_institution IS
    'v6 Dashboard — agrégats par institution (volume, mode, statuts). Utilisée par GET /api/admin/institutions.';

-- ── 7.5 Fonction fn_refresh_dashboard_metrics — Agrégation quotidienne ────────
-- UPSERT atomique des métriques du jour dans dashboard_metrics_daily.
-- Appelée chaque soir par APScheduler (Retry Worker backend FastAPI).
-- Usage : SELECT fn_refresh_dashboard_metrics();        -- aujourd'hui
--         SELECT fn_refresh_dashboard_metrics('2026-03-09'); -- date spécifique
CREATE OR REPLACE FUNCTION public.fn_refresh_dashboard_metrics(
    p_date DATE DEFAULT CURRENT_DATE
) RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO public.dashboard_metrics_daily (
        metric_date,
        nb_diplomes_emis,
        nb_diplomes_microservice,
        nb_diplomes_upload,
        nb_nouveaux_etudiants,
        nb_institutions_actives,
        nb_diplomes_confirmes,
        nb_diplomes_pending,
        nb_diplomes_revoques,
        nb_verifications,
        updated_at
    )
    SELECT
        p_date,
        COUNT(*),
        COUNT(CASE WHEN d.generation_mode = 'MICROSERVICE' THEN 1 END),
        COUNT(CASE WHEN d.generation_mode = 'UPLOAD'       THEN 1 END),
        -- Nouveaux étudiants inscrits ce jour (via user_ext.created_at)
        (SELECT COUNT(*)
         FROM public.user_ext ue
         JOIN public."UserRole" ur ON ur.user_id = ue.user_id
         JOIN public."ROLE" r      ON r.id_role   = ur.role_id
         WHERE r.code = 'ETUDIANT' AND DATE(ue.created_at) = p_date),
        COUNT(DISTINCT d.institution_id),
        COUNT(CASE WHEN d.statut = 'ORIGINAL'          THEN 1 END),
        -- Total global des PENDING (pas limité au jour)
        (SELECT COUNT(*) FROM public.diplome_blockchain_ext
         WHERE statut = 'PENDING_BLOCKCHAIN'),
        COUNT(CASE WHEN d.statut = 'REVOQUE'            THEN 1 END),
        -- Nombre de vérifications QR effectuées ce jour
        (SELECT COUNT(*)
         FROM public.historique_operations h
         WHERE h.type_operation = 'VERIFICATION'
           AND DATE(h."timestamp") = p_date),
        NOW()
    FROM public.diplome_blockchain_ext d
    WHERE DATE(d.date_emission) = p_date
    ON CONFLICT (metric_date) DO UPDATE SET
        nb_diplomes_emis         = EXCLUDED.nb_diplomes_emis,
        nb_diplomes_microservice = EXCLUDED.nb_diplomes_microservice,
        nb_diplomes_upload       = EXCLUDED.nb_diplomes_upload,
        nb_nouveaux_etudiants    = EXCLUDED.nb_nouveaux_etudiants,
        nb_institutions_actives  = EXCLUDED.nb_institutions_actives,
        nb_diplomes_confirmes    = EXCLUDED.nb_diplomes_confirmes,
        nb_diplomes_pending      = EXCLUDED.nb_diplomes_pending,
        nb_diplomes_revoques     = EXCLUDED.nb_diplomes_revoques,
        nb_verifications         = EXCLUDED.nb_verifications,
        updated_at               = NOW();

    RAISE NOTICE 'Métriques du % rafraîchies avec succès.', p_date;
END;
$$;

COMMENT ON FUNCTION public.fn_refresh_dashboard_metrics(DATE) IS
    'v6 Dashboard Super Admin — UPSERT atomique des métriques quotidiennes. Appelée par APScheduler chaque soir. Idempotente : relancer = recalcul propre.';


COMMIT;
