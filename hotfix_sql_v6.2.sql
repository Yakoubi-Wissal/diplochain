-- ═══════════════════════════════════════════════════════════════════════════
-- DiploChain v6.2 — Hotfix SQL
-- Bugs corrigés :
--   Bug #8 : fn_refresh_dashboard_metrics ne compte pas statut='CONFIRME'
--   Bug #8 : v_diplomas_per_student ne compte pas statut='CONFIRME'
--   Bug #9 : requêtes audit corrigées (timestamp, pas created_at)
-- ═══════════════════════════════════════════════════════════════════════════


-- ── 1. Corriger fn_refresh_dashboard_metrics ─────────────────────────────────
-- Avant : COUNT(CASE WHEN d.statut = 'ORIGINAL' ...)
-- Après : COUNT(CASE WHEN d.statut IN ('ORIGINAL', 'CONFIRME') ...)

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
        -- Nouveaux étudiants inscrits ce jour
        (SELECT COUNT(*)
         FROM public.user_ext ue
         JOIN public."UserRole" ur ON ur.user_id = ue.user_id
         JOIN public."ROLE" r      ON r.id_role   = ur.role_id
         WHERE r.code = 'ETUDIANT' AND DATE(ue.created_at) = p_date),
        COUNT(DISTINCT d.institution_id),
        -- FIX Bug #8 : compter ORIGINAL (v5) ET CONFIRME (v6.1 service)
        COUNT(CASE WHEN d.statut IN ('ORIGINAL', 'CONFIRME') THEN 1 END),
        -- Total global des PENDING (pas limité au jour)
        (SELECT COUNT(*) FROM public.diplome_blockchain_ext
         WHERE statut = 'PENDING_BLOCKCHAIN'),
        COUNT(CASE WHEN d.statut = 'REVOQUE' THEN 1 END),
        -- Vérifications QR — FIX Bug #9 : colonne "timestamp" (pas created_at)
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
    'v6.2 Hotfix — Corrige Bug #8 : compte ORIGINAL et CONFIRME comme diplômes confirmés.';


-- ── 2. Corriger la vue v_diplomas_per_student ─────────────────────────────────
-- FIX Bug #8 : nb_confirmes doit compter ORIGINAL et CONFIRME

CREATE OR REPLACE VIEW public.v_diplomas_per_student AS
SELECT
    e.etudiant_id,
    e.nom,
    e.prenom,
    e.email_etudiant                                                     AS email,
    ue.numero_etudiant,
    COUNT(ed.id_diplome)                                                 AS nb_diplomes_total,
    -- FIX : compter les deux valeurs de statut "confirmé"
    COUNT(CASE WHEN dbe.statut IN ('ORIGINAL', 'CONFIRME') THEN 1 END)  AS nb_confirmes,
    COUNT(CASE WHEN dbe.statut = 'PENDING_BLOCKCHAIN'      THEN 1 END)  AS nb_pending,
    COUNT(CASE WHEN dbe.statut = 'REVOQUE'                 THEN 1 END)  AS nb_revoques,
    MAX(dbe.date_emission)                                               AS derniere_emission
FROM public.etudiant e
LEFT JOIN public.user_ext ue           ON ue.user_id = e.id_user
LEFT JOIN public.etudiant_diplome ed   ON ed.etudiant_id = e.etudiant_id
LEFT JOIN public.diplome_blockchain_ext dbe ON dbe.id_diplome = ed.id_diplome
GROUP BY e.etudiant_id, e.nom, e.prenom, e.email_etudiant, ue.numero_etudiant
ORDER BY nb_diplomes_total DESC;

COMMENT ON VIEW public.v_diplomas_per_student IS
    'v6.2 Hotfix — Bug #8 corrigé : nb_confirmes compte ORIGINAL et CONFIRME.';


-- ── 3. Recalculer toutes les métriques existantes ────────────────────────────
-- À exécuter après le déploiement du hotfix pour corriger les lignes existantes.

DO $$
DECLARE
    d DATE;
BEGIN
    FOR d IN SELECT DISTINCT metric_date FROM dashboard_metrics_daily ORDER BY metric_date
    LOOP
        PERFORM fn_refresh_dashboard_metrics(d);
        RAISE NOTICE 'Recalculé : %', d;
    END LOOP;
END;
$$;


-- ── 4. Requête de vérification post-hotfix ────────────────────────────────────
-- Exécuter pour valider que les métriques sont maintenant cohérentes.

SELECT
    d.metric_date,
    d.nb_diplomes_confirmes                                           AS metric_confirmes,
    COUNT(CASE WHEN ext.statut IN ('ORIGINAL','CONFIRME') THEN 1 END) AS real_confirmes,
    CASE
        WHEN d.nb_diplomes_confirmes =
             COUNT(CASE WHEN ext.statut IN ('ORIGINAL','CONFIRME') THEN 1 END)
        THEN '✅ OK'
        ELSE '❌ ECART'
    END AS coherence
FROM dashboard_metrics_daily d
LEFT JOIN diplome_blockchain_ext ext ON DATE(ext.date_emission) = d.metric_date
GROUP BY d.metric_date, d.nb_diplomes_confirmes
ORDER BY d.metric_date DESC;
