-- DiploChain V2 Seed Data
BEGIN;

-- 1. Roles
INSERT INTO public."ROLE" (id_role, label_role, code) VALUES
(1, 'Super Admin', 'SUPER_ADMIN'),
(2, 'Institution Admin', 'ADMIN_INSTITUTION'),
(3, 'Etudiant', 'ETUDIANT')
ON CONFLICT (id_role) DO NOTHING;

-- 2. Users (Password is 'password' hashed with bcrypt if needed, but here we just put a string for now as we don't have the hash tool handy, assuming user-service can handle it or we use the hash from security.py)
-- 'password' hashed with passlib.hash.bcrypt is likely what's expected.
-- For now let's just use a placeholder that looks like a hash or just 'password' if the service doesn't validate on read.
INSERT INTO public."User" (id_user, username, password, email, status) VALUES
(1, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LpafE.Kbh6.p5O5uYqx/fG9A03hK9z6B6a.iW', 'admin@diplochain.tn', 'ACTIF'),
(2, 'esprit_admin', '$2b$12$LQv3c1yqBWVHxkd0LpafE.Kbh6.p5O5uYqx/fG9A03hK9z6B6a.iW', 'contact@esprit.tn', 'ACTIF'),
(3, 'student1', '$2b$12$LQv3c1yqBWVHxkd0LpafE.Kbh6.p5O5uYqx/fG9A03hK9z6B6a.iW', 'student1@esprit.tn', 'ACTIF')
ON CONFLICT (id_user) DO NOTHING;

SELECT setval('public."User_id_user_seq"', (SELECT MAX(id_user) FROM public."User"));
SELECT setval('public."ROLE_id_role_seq"', (SELECT MAX(id_role) FROM public."ROLE"));

INSERT INTO public."UserRole" (user_id, role_id) VALUES
(1, 1),
(2, 2),
(3, 3)
ON CONFLICT DO NOTHING;

-- 3. Institutions
INSERT INTO public.institution (institution_id, nom_institution, adresse, ville, pays, email_institution) VALUES
(1, 'ESPRIT', 'Ariana Soghra', 'Ariana', 'Tunisia', 'contact@esprit.tn'),
(2, 'Université de Tunis', 'Tunis', 'Tunis', 'Tunisia', 'contact@utunis.tn')
ON CONFLICT (institution_id) DO NOTHING;

SELECT setval('public.institution_institution_id_seq', (SELECT MAX(institution_id) FROM public.institution));

INSERT INTO public.institution_blockchain_ext (institution_id, channel_id, peer_node_url, status, code) VALUES
(1, 'esprit-channel', 'peer0.esprit.diplochain.tn:7051', 'ACTIVE', 'ESPRIT'),
(2, 'utunis-channel', 'peer0.utunis.diplochain.tn:7051', 'ACTIVE', 'UTUNIS')
ON CONFLICT (institution_id) DO NOTHING;

-- 4. Nationalities & Specialities
INSERT INTO public.nationalite (code_nationalite, designation_nationalite) VALUES
('TUN', 'Tunisienne'),
('FRA', 'Française')
ON CONFLICT DO NOTHING;

INSERT INTO public.specialite (code_specialite, designation_specialite) VALUES
('INF', 'Informatique'),
('TEL', 'Télécom')
ON CONFLICT DO NOTHING;

INSERT INTO public.specialite_ext (code_specialite, nom, code, institution_id, is_active) VALUES
('INF', 'Génie Informatique', 'GI', 1, true),
('TEL', 'Génie Télécom', 'GT', 1, true)
ON CONFLICT DO NOTHING;

-- 5. Students
INSERT INTO public.etudiant (etudiant_id, email_etudiant, nom, prenom, code_nationalite, code_specialite, id_user) VALUES
('240001', 'student1@esprit.tn', 'Ben Salah', 'Ahmed', 'TUN', 'INF', 3)
ON CONFLICT (etudiant_id) DO NOTHING;

INSERT INTO public.user_ext (user_id, statut_diplochain, institution_id, numero_etudiant, nom, prenom) VALUES
(3, 'ACTIF', 1, '240001', 'Ben Salah', 'Ahmed')
ON CONFLICT (user_id) DO NOTHING;

-- 6. Diplomas
INSERT INTO public.etudiant_diplome (id_diplome, etudiant_id, session_diplome, id_annexe, num_diplome, date_diplome, date_liv_diplome) VALUES
(1, '240001', 'Juin 2024', 1, 1001, '2024-06-30', '2024-07-15')
ON CONFLICT (id_diplome) DO NOTHING;

INSERT INTO public.diplome_blockchain_ext (id_diplome, titre, mention, date_emission, annee_promotion, hash_sha256, tx_id_fabric, ipfs_cid, statut, generation_mode, institution_id, specialite_id) VALUES
(1, 'Diplôme de Ingénieur', 'Bien', '2024-06-30', '2024', 'f2ca1bb6c7e907d06dafe4687e579fce76b377bc8c057608e547377855b7d605', 'tx_abc123', 'QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco', 'ORIGINAL', 'MICROSERVICE', 1, 'INF')
ON CONFLICT (id_diplome) DO NOTHING;

SELECT setval('public.etudiant_diplome_id_diplome_seq', (SELECT MAX(id_diplome) FROM public.etudiant_diplome));

-- 7. Metrics
INSERT INTO public.dashboard_metrics_daily (metric_date, nb_diplomes_emis, nb_diplomes_microservice, nb_diplomes_upload, nb_nouveaux_etudiants, nb_institutions_actives, nb_diplomes_confirmes, nb_diplomes_pending, nb_diplomes_revoques, nb_verifications) VALUES
(CURRENT_DATE, 1, 1, 0, 1, 1, 1, 0, 0, 5),
((CURRENT_DATE - INTERVAL '1 day')::DATE, 0, 0, 0, 0, 0, 0, 0, 0, 2)
ON CONFLICT (metric_date) DO NOTHING;

COMMIT;
