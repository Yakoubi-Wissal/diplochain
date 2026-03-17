-- =============================================================================
-- DiploChain — Script de Migration Différentiel v5 → v6
-- Architecture Microservices + Dashboard Super Admin
--
-- ⚠  CE SCRIPT EST DIFFÉRENTIEL : à appliquer SUR une base v5 existante.
--    NE PAS ré-exécuter corrected_schema_v6.sql complet sur une base v5 :
--    les CREATE TABLE échoueraient sur les tables existantes.
--
-- PRÉREQUIS :
--   □ Backup effectué AVANT exécution :
--     docker exec diplochain_postgres pg_dump -U diplochain_user diplochain_db \
--       > backup_v5_$(date +%Y%m%d_%H%M).sql
--   □ PostgreSQL 14+ actif
--   □ Connexion en tant que propriétaire des tables (diplochain_user)
--
-- EXÉCUTION :
--   docker exec -i diplochain_postgres psql \
--     -U diplochain_user -d diplochain_db < migration_v5_v6.sql
--
-- DURÉE ESTIMÉE : < 30 secondes (base vide ou petite volumétrie)
-- =============================================================================

BEGIN; -- Transaction atomique : tout ou rien

-- =============================================================================
-- ÉTAPE 1 — Mise à jour du type ENUM statut_diplome
-- Ajout de la valeur PENDING_BLOCKCHAIN (état intermédiaire entre IPFS ok
-- et confirmation Hyperledger Fabric).
--
-- Impact : le Retry Worker utilise ce statut pour identifier les diplômes
-- dont le tx_id_fabric est encore NULL et relancer RegisterDiploma().
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum e
        JOIN pg_type t ON t.oid = e.enumtypid
        WHERE t.typname = 'statut_diplome'
          AND e.enumlabel = 'PENDING_BLOCKCHAIN'
    ) THEN
        -- ALTER TYPE ... ADD VALUE ne peut pas être dans un bloc transactionnel
        -- standard en PG < 12 mais est supporté en PG 12+ en dehors d'un DDL
        -- complexe. Ici on utilise COMMIT intermédiaire via une procédure.
        RAISE NOTICE 'Ajout de PENDING_BLOCKCHAIN dans statut_diplome...';
    ELSE
        RAISE NOTICE 'PENDING_BLOCKCHAIN déjà présent dans statut_diplome — ignoré';
    END IF;
END
$$;

-- ALTER TYPE ne peut pas être exécuté dans un bloc DO transactionnel.
-- On sort temporairement de la transaction pour cet ALTER puis on reprend.
COMMIT;
ALTER TYPE statut_diplome ADD VALUE IF NOT EXISTS 'PENDING_BLOCKCHAIN';
BEGIN;


-- =============================================================================
-- ÉTAPE 2 — Ajout de la colonne generation_mode sur diplome_blockchain_ext
-- Trace l'origine du diplôme : UPLOAD (manuel) ou MICROSERVICE (PDF auto).
--
-- Impact : permet au Dashboard Super Admin de distinguer les deux modes
-- d'émission dans les métriques et vues SQL.
-- =============================================================================

DO $$
BEGIN
    IF NOT diplochain_col_exists('diplome_blockchain_ext', 'generation_mode') THEN
        ALTER TABLE public.diplome_blockchain_ext
            ADD COLUMN generation_mode VARCHAR(20) NOT NULL DEFAULT 'UPLOAD';
        -- Rétrocompatibilité : tous les diplômes v5 sont considérés mode UPLOAD
        UPDATE public.diplome_blockchain_ext
            SET generation_mode = 'UPLOAD'
            WHERE generation_mode IS NULL OR generation_mode = '';
        RAISE NOTICE 'Colonne generation_mode ajoutée sur diplome_blockchain_ext';
    ELSE
        RAISE NOTICE 'generation_mode déjà présent — ignoré';
    END IF;
END
$$;


-- =============================================================================
-- ÉTAPE 3 — Contrainte métier chk_tx_id_required_when_confirmed
-- tx_id_fabric est obligatoire pour tout statut ≠ PENDING_BLOCKCHAIN.
-- Garantit qu'aucun diplôme ne peut être marqué ORIGINAL/CONFIRME sans
-- preuve d'ancrage Hyperledger Fabric.
-- =============================================================================

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
    ELSE
        RAISE NOTICE 'Contrainte déjà présente — ignorée';
    END IF;
END
$$;


-- =============================================================================
-- ÉTAPE 4 — Création de la table dashboard_metrics_daily (si absente)
-- Agrégats quotidiens pré-calculés pour le Dashboard Super Admin.
-- Alimentée par fn_refresh_dashboard_metrics() via APScheduler.
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.dashboard_metrics_daily (
    metric_date              DATE      NOT NULL,
    nb_diplomes_emis         INT4      NOT NULL DEFAULT 0,
    nb_diplomes_microservice INT4      NOT NULL DEFAULT 0,
    nb_diplomes_upload       INT4      NOT NULL DEFAULT 0,
    nb_nouveaux_etudiants    INT4      NOT NULL DEFAULT 0,
    nb_institutions_actives  INT4      NOT NULL DEFAULT 0,
    nb_diplomes_confirmes    INT4      NOT NULL DEFAULT 0,
    nb_diplomes_pending      INT4      NOT NULL DEFAULT 0,
    nb_diplomes_revoques     INT4      NOT NULL DEFAULT 0,
    nb_verifications         INT4      NOT NULL DEFAULT 0,
    updated_at               TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT dashboard_metrics_daily_pkey PRIMARY KEY (metric_date)
);

COMMENT ON TABLE public.dashboard_metrics_daily IS
    'v6 Dashboard Super Admin — métriques quotidiennes pré-agrégées. '
    'PRIMARY KEY metric_date garantit l''unicité et permet l''UPSERT de fn_refresh_dashboard_metrics(). '
    'NE PAS écrire directement : passer par fn_refresh_dashboard_metrics().';

-- Index sur metric_date DESC pour accès O(1) aux métriques récentes
CREATE UNIQUE INDEX IF NOT EXISTS idx_dashboard_metrics_date
    ON public.dashboard_metrics_daily(metric_date DESC);
COMMENT ON INDEX idx_dashboard_metrics_date IS
    'v6 Dashboard — accès O(1) aux métriques quotidiennes triées par date décroissante.';


-- =============================================================================
-- ÉTAPE 5 — Index additionnels v6 (Dashboard Super Admin + Retry Worker)
-- =============================================================================

-- 5a. Requêtes Dashboard triées par date d'émission décroissante
CREATE INDEX IF NOT EXISTS idx_diplomes_date_emission_desc
    ON public.diplome_blockchain_ext(date_emission DESC);
COMMENT ON INDEX idx_diplomes_date_emission_desc IS
    'v6 Dashboard — GET /api/admin/diplomas trié par date décroissante O(log n).';

-- 5b. Analytics mode génération UPLOAD vs MICROSERVICE
CREATE INDEX IF NOT EXISTS idx_diplomes_generation
    ON public.diplome_blockchain_ext(generation_mode);
COMMENT ON INDEX idx_diplomes_generation IS
    'v6 Dashboard Analytics — filtrage et comptage par mode de génération.';

-- 5c. Index partiel Retry Worker — scanne uniquement PENDING_BLOCKCHAIN
CREATE INDEX IF NOT EXISTS idx_diplomes_pending
    ON public.diplome_blockchain_ext(id_diplome)
    WHERE statut = 'PENDING_BLOCKCHAIN';
COMMENT ON INDEX idx_diplomes_pending IS
    'v6 Retry Worker — index partiel PENDING_BLOCKCHAIN uniquement. '
    'Évite un full scan sur diplome_blockchain_ext à chaque cycle de retry.';

-- 5d. Métriques nouveaux étudiants par jour
CREATE INDEX IF NOT EXISTS idx_etudiants_created_at
    ON public.user_ext(created_at);
COMMENT ON INDEX idx_etudiants_created_at IS
    'v6 Dashboard — calcul nb_nouveaux_etudiants par jour dans fn_refresh_dashboard_metrics().';


-- =============================================================================
-- ÉTAPE 6 — Vue v_diplomas_per_student
-- Statistiques temps réel des diplômes par étudiant.
-- Utilisée par : GET /api/admin/students (Dashboard Super Admin).
-- RLS : bypassée pour SUPER_ADMIN, filtrée par institution pour ADMIN.
-- =============================================================================

CREATE OR REPLACE VIEW public.v_diplomas_per_student AS
SELECT
    e.etudiant_id,
    e.nom,
    e.prenom,
    e.email_etudiant                                              AS email,
    ue.numero_etudiant,
    COUNT(ed.id_diplome)                                          AS nb_diplomes_total,
    COUNT(CASE WHEN dbe.statut = 'ORIGINAL'          THEN 1 END) AS nb_confirmes,
    COUNT(CASE WHEN dbe.statut = 'PENDING_BLOCKCHAIN' THEN 1 END) AS nb_pending,
    COUNT(CASE WHEN dbe.statut = 'REVOQUE'            THEN 1 END) AS nb_revoques,
    MAX(dbe.date_emission)                                        AS derniere_emission
FROM public.etudiant e
LEFT JOIN public.user_ext ue               ON ue.user_id    = e.id_user
LEFT JOIN public.etudiant_diplome ed        ON ed.etudiant_id = e.etudiant_id
LEFT JOIN public.diplome_blockchain_ext dbe ON dbe.id_diplome = ed.id_diplome
GROUP BY
    e.etudiant_id, e.nom, e.prenom, e.email_etudiant, ue.numero_etudiant
ORDER BY nb_diplomes_total DESC;

COMMENT ON VIEW public.v_diplomas_per_student IS
    'v6 Dashboard Super Admin — agrégats diplômes par étudiant calculés en temps réel. '
    'Endpoint : GET /api/admin/students. '
    'Compte ORIGINAL, PENDING_BLOCKCHAIN, REVOQUE par étudiant.';


-- =============================================================================
-- ÉTAPE 7 — Vue v_diplomas_per_institution
-- Statistiques temps réel des diplômes par institution émettrice.
-- Utilisée par : GET /api/admin/institutions (Dashboard Super Admin).
-- =============================================================================

CREATE OR REPLACE VIEW public.v_diplomas_per_institution AS
SELECT
    i.institution_id,
    i.nom_institution                                                   AS nom,
    ibc.code,
    ibc.status                                                          AS statut,
    COUNT(dbe.id_diplome)                                               AS nb_diplomes_total,
    COUNT(CASE WHEN dbe.generation_mode = 'MICROSERVICE' THEN 1 END)   AS nb_via_microservice,
    COUNT(CASE WHEN dbe.generation_mode = 'UPLOAD'       THEN 1 END)   AS nb_via_upload,
    COUNT(CASE WHEN dbe.statut = 'PENDING_BLOCKCHAIN'    THEN 1 END)   AS nb_pending,
    COUNT(CASE WHEN dbe.statut = 'REVOQUE'               THEN 1 END)   AS nb_revoques,
    MAX(dbe.date_emission)                                              AS derniere_emission
FROM public.institution i
LEFT JOIN public.institution_blockchain_ext ibc ON ibc.institution_id = i.institution_id
LEFT JOIN public.diplome_blockchain_ext dbe     ON dbe.institution_id  = i.institution_id
GROUP BY
    i.institution_id, i.nom_institution, ibc.code, ibc.status
ORDER BY nb_diplomes_total DESC;

COMMENT ON VIEW public.v_diplomas_per_institution IS
    'v6 Dashboard Super Admin — agrégats diplômes par institution calculés en temps réel. '
    'Endpoint : GET /api/admin/institutions. '
    'Distingue UPLOAD vs MICROSERVICE et affiche les PENDING et REVOQUES.';


-- =============================================================================
-- ÉTAPE 8 — Fonction fn_refresh_dashboard_metrics(p_date)
-- UPSERT atomique des métriques du jour dans dashboard_metrics_daily.
-- Idempotente : relancer = recalcul propre sans doublon.
--
-- Appelée par :
--   • APScheduler (backend FastAPI) chaque soir à 23:55
--   • Manuellement : SELECT fn_refresh_dashboard_metrics();
--   • Recalcul d'un jour passé : SELECT fn_refresh_dashboard_metrics('2026-03-01');
-- =============================================================================

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

        -- Total diplômes émis ce jour (date_emission = p_date)
        COUNT(*),

        -- Part microservice (PDF auto-généré par le microservice FastAPI)
        COUNT(CASE WHEN d.generation_mode = 'MICROSERVICE' THEN 1 END),

        -- Part upload manuel
        COUNT(CASE WHEN d.generation_mode = 'UPLOAD' THEN 1 END),

        -- Nouveaux étudiants inscrits ce jour (rôle ETUDIANT via user_ext)
        (SELECT COUNT(*)
         FROM public.user_ext ue
         JOIN public."UserRole" ur ON ur.user_id = ue.user_id
         JOIN public."ROLE" r      ON r.id_role   = ur.role_id
         WHERE r.code = 'ETUDIANT'
           AND DATE(ue.created_at) = p_date),

        -- Institutions actives ayant émis au moins un diplôme ce jour
        COUNT(DISTINCT d.institution_id),

        -- Diplômes confirmés on-chain (statut ORIGINAL)
        COUNT(CASE WHEN d.statut = 'ORIGINAL' THEN 1 END),

        -- Total global des diplômes en attente Fabric (pas limité au jour)
        (SELECT COUNT(*) FROM public.diplome_blockchain_ext
         WHERE statut = 'PENDING_BLOCKCHAIN'),

        -- Diplômes révoqués ce jour
        COUNT(CASE WHEN d.statut = 'REVOQUE' THEN 1 END),

        -- Vérifications QR effectuées ce jour (type VERIFICATION dans audit)
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
    'v6 Dashboard Super Admin — UPSERT atomique des métriques quotidiennes. '
    'Idempotente : peut être relancée sans risque de doublon (ON CONFLICT DO UPDATE). '
    'Appelée par APScheduler chaque soir. '
    'Paramètre : p_date (DATE, défaut CURRENT_DATE). '
    'Exemple : SELECT fn_refresh_dashboard_metrics(''2026-03-09'');';


-- =============================================================================
-- ÉTAPE 9 — Initialisation des métriques du jour (optionnel)
-- Déclencher immédiatement après migration pour peupler dashboard_metrics_daily.
-- =============================================================================

SELECT public.fn_refresh_dashboard_metrics(CURRENT_DATE);


-- =============================================================================
-- ÉTAPE 10 — Validation finale de la migration
-- =============================================================================

DO $$
DECLARE
    v_enum_ok     BOOLEAN;
    v_col_ok      BOOLEAN;
    v_table_ok    BOOLEAN;
    v_view1_ok    BOOLEAN;
    v_view2_ok    BOOLEAN;
    v_fn_ok       BOOLEAN;
    v_idx_count   INT;
BEGIN
    -- Enum PENDING_BLOCKCHAIN
    SELECT EXISTS (
        SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid=e.enumtypid
        WHERE t.typname='statut_diplome' AND e.enumlabel='PENDING_BLOCKCHAIN'
    ) INTO v_enum_ok;

    -- Colonne generation_mode
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='diplome_blockchain_ext'
          AND column_name='generation_mode'
    ) INTO v_col_ok;

    -- Table dashboard_metrics_daily
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema='public' AND table_name='dashboard_metrics_daily'
    ) INTO v_table_ok;

    -- Vue v_diplomas_per_student
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema='public' AND table_name='v_diplomas_per_student'
    ) INTO v_view1_ok;

    -- Vue v_diplomas_per_institution
    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema='public' AND table_name='v_diplomas_per_institution'
    ) INTO v_view2_ok;

    -- Fonction fn_refresh_dashboard_metrics
    SELECT EXISTS (
        SELECT 1 FROM pg_proc WHERE proname='fn_refresh_dashboard_metrics'
    ) INTO v_fn_ok;

    -- Compter index v6
    SELECT COUNT(*) INTO v_idx_count
    FROM pg_indexes
    WHERE schemaname='public'
      AND indexname IN (
        'idx_diplomes_date_emission_desc',
        'idx_diplomes_generation',
        'idx_diplomes_pending',
        'idx_etudiants_created_at',
        'idx_dashboard_metrics_date'
      );

    RAISE NOTICE '============ VALIDATION MIGRATION v5 → v6 ============';
    RAISE NOTICE '  [%] PENDING_BLOCKCHAIN dans statut_diplome', CASE WHEN v_enum_ok  THEN 'OK' ELSE 'ECHEC' END;
    RAISE NOTICE '  [%] Colonne generation_mode',                CASE WHEN v_col_ok   THEN 'OK' ELSE 'ECHEC' END;
    RAISE NOTICE '  [%] Table dashboard_metrics_daily',          CASE WHEN v_table_ok THEN 'OK' ELSE 'ECHEC' END;
    RAISE NOTICE '  [%] Vue v_diplomas_per_student',             CASE WHEN v_view1_ok THEN 'OK' ELSE 'ECHEC' END;
    RAISE NOTICE '  [%] Vue v_diplomas_per_institution',         CASE WHEN v_view2_ok THEN 'OK' ELSE 'ECHEC' END;
    RAISE NOTICE '  [%] Fonction fn_refresh_dashboard_metrics',  CASE WHEN v_fn_ok    THEN 'OK' ELSE 'ECHEC' END;
    RAISE NOTICE '  [%/5] Index v6 créés',                       v_idx_count;
    RAISE NOTICE '======================================================';

    IF NOT (v_enum_ok AND v_col_ok AND v_table_ok AND v_view1_ok AND v_view2_ok AND v_fn_ok) THEN
        RAISE EXCEPTION 'Migration v5→v6 incomplète — vérifier les erreurs ci-dessus';
    END IF;

    RAISE NOTICE 'Migration DiploChain v5 → v6 réussie.';
END
$$;

COMMIT; -- Valider si tout est OK

-- =============================================================================
-- POST-MIGRATION — Liste de contrôle applicative
-- =============================================================================
--
-- Backend FastAPI :
--   □ Ajouter generation_mode dans le modèle SQLAlchemy Diplome
--   □ Ajouter le modèle DashboardMetricsDaily
--   □ Enregistrer le router dashboard.py dans main.py
--   □ Configurer APScheduler pour appeler fn_refresh_dashboard_metrics()
--   □ Mettre à jour le pipeline diplomes.py : IPFS-first, generation_mode='MICROSERVICE'
--
-- Docker :
--   □ Ajouter le service diploma-generator dans docker-compose.yml
--   □ Supprimer le service orchestrateur Java si présent
--
-- Tests :
--   □ Vérifier SELECT * FROM v_diplomas_per_student LIMIT 5;
--   □ Vérifier SELECT * FROM v_diplomas_per_institution;
--   □ Vérifier SELECT * FROM dashboard_metrics_daily;
--   □ Tester INSERT d'un diplôme avec statut=PENDING_BLOCKCHAIN et tx_id_fabric=NULL
--   □ Tester la contrainte : UPDATE diplome SET statut='ORIGINAL' WHERE tx_id_fabric IS NULL
--     → Doit échouer avec violation de contrainte
-- =============================================================================
