// centralise les données factices utilisées par le dashboard
// les tableaux STATUTS_PIE/MODE_PIE restent dans le composant car ils dépendent
// des tokens de design (T) définis dans le même fichier.

/**
 * @typedef {Object} MetricsToday
 * @property {string} metric_date
 * @property {number} nb_diplomes_emis
 * @property {number} nb_diplomes_microservice
 * @property {number} nb_diplomes_upload
 * @property {number} nb_nouveaux_etudiants
 * @property {number} nb_institutions_actives
 * @property {number} nb_diplomes_confirmes
 * @property {number} nb_diplomes_pending
 * @property {number} nb_diplomes_revoques
 * @property {number} nb_verifications
 * @property {string} updated_at
 */

/**
 * @typedef {Object} Institution
 * @property {number} institution_id
 * @property {string} nom
 * @property {string} code
 * @property {string} statut
 * @property {number} nb_diplomes_total
 * @property {number} nb_via_microservice
 * @property {number} nb_via_upload
 * @property {number} nb_pending
 * @property {number} nb_revoques
 * @property {string} derniere_emission
 */

/**
 * @typedef {Object} Student
 * @property {string} etudiant_id
 * @property {string} nom
 * @property {string} prenom
 * @property {string} email
 * @property {string} numero_etudiant
 * @property {number} nb_diplomes_total
 * @property {number} nb_confirmes
 * @property {number} nb_pending
 * @property {number} nb_revoques
 * @property {string} derniere_emission
 */

/**
 * @typedef {Object} Diploma
 * @property {number} id
 * @property {string} etudiant
 * @property {string} titre
 * @property {string} inst
 * @property {string} statut
 * @property {string} generation_mode
 * @property {string} date
 */

/**
 * @typedef {Object} RetryAlert
 * @property {number} id
 * @property {string} etudiant
 * @property {string} hash
 * @property {number} retry
 * @property {string} age
 * @property {string} inst
 * @property {boolean} urgent
 */

/**
 * @typedef {Object} PendingAlert
 * @property {number} id
 * @property {string} etudiant
 * @property {string} hash
 * @property {number} retry
 * @property {string} age
 * @property {string} inst
 */

/**
 * @typedef {Object} AuditEntry
 * @property {string} type_operation
 * @property {string} acteur
 * @property {string} diplome_id
 * @property {string} timestamp
 * @property {string} inst
 * @property {string} color
 */

/**
 * @typedef {Object} ValidationRequest
 * @property {number} entreprise_validation_id
 * @property {number} entreprise_id
 * @property {string} nom_entreprise
 * @property {string} ms_tenant_id
 * @property {string} microsoft_email_domain
 * @property {string} status
 * @property {string} demande_at
 * @property {string|null} traite_par
 * @property {string|null} motif_refus
 */

/**
 * @typedef {Object} Entreprise
 * @property {number} entreprise_id
 * @property {string} nom
 * @property {string} microsoft_tenant_id
 * @property {string} microsoft_email_domain
 * @property {string} status
 * @property {number} nb_verifications
 * @property {string|null} derniere_session
 * @property {boolean} is_valid
 */

/**
 * @typedef {Object} AuthSession
 * @property {number} session_id
 * @property {number} entreprise_id
 * @property {string} nom_entreprise
 * @property {string} microsoft_email
 * @property {string} tenant_id
 * @property {string} expires_at
 * @property {boolean} is_valid
 */

export const MOCK_METRICS_TODAY = {
  metric_date: "2026-03-11",
  nb_diplomes_emis: 847, nb_diplomes_microservice: 235, nb_diplomes_upload: 612,
  nb_nouveaux_etudiants: 142, nb_institutions_actives: 7,
  nb_diplomes_confirmes: 801, nb_diplomes_pending: 23, nb_diplomes_revoques: 23,
  nb_verifications: 2341, updated_at: "2026-03-11T12:00:00",
};

export const MOCK_METRICS_DAILY = [
  { mois:"Sep", nb_diplomes_emis:62,  nb_diplomes_confirmes:59,  nb_verifications:180 },
  { mois:"Oct", nb_diplomes_emis:88,  nb_diplomes_confirmes:84,  nb_verifications:241 },
  { mois:"Nov", nb_diplomes_emis:74,  nb_diplomes_confirmes:71,  nb_verifications:198 },
  { mois:"Déc", nb_diplomes_emis:43,  nb_diplomes_confirmes:41,  nb_verifications:112 },
  { mois:"Jan", nb_diplomes_emis:105, nb_diplomes_confirmes:98,  nb_verifications:312 },
  { mois:"Fév", nb_diplomes_emis:127, nb_diplomes_confirmes:120, nb_verifications:387 },
  { mois:"Mar", nb_diplomes_emis:156, nb_diplomes_confirmes:148, nb_verifications:451 },
];

export const MOCK_INSTITUTIONS = [
  { institution_id:1, nom:"ESPRIT School of Engineering", code:"ESP", statut:"ACTIVE",    nb_diplomes_total:312, nb_via_microservice:180, nb_via_upload:132, nb_pending:8, nb_revoques:4, derniere_emission:"2026-03-10" },
  { institution_id:2, nom:"Université de Tunis El Manar", code:"UTM", statut:"ACTIVE",    nb_diplomes_total:187, nb_via_microservice:90,  nb_via_upload:97,  nb_pending:5, nb_revoques:3, derniere_emission:"2026-03-09" },
  { institution_id:3, nom:"INSAT",                        code:"INS", statut:"ACTIVE",    nb_diplomes_total:143, nb_via_microservice:70,  nb_via_upload:73,  nb_pending:4, nb_revoques:2, derniere_emission:"2026-03-09" },
  { institution_id:4, nom:"ENIT",                         code:"ENI", statut:"ACTIVE",    nb_diplomes_total:98,  nb_via_microservice:40,  nb_via_upload:58,  nb_pending:3, nb_revoques:1, derniere_emission:"2026-03-08" },
  { institution_id:5, nom:"Polytechnique Tunis",          code:"EPT", statut:"ACTIVE",    nb_diplomes_total:67,  nb_via_microservice:30,  nb_via_upload:37,  nb_pending:2, nb_revoques:0, derniere_emission:"2026-03-07" },
  { institution_id:6, nom:"ISG Tunis",                    code:"ISG", statut:"SUSPENDUE", nb_diplomes_total:24,  nb_via_microservice:10,  nb_via_upload:14,  nb_pending:1, nb_revoques:1, derniere_emission:"2026-02-20" },
  { institution_id:7, nom:"ISET Charguia",                code:"IST", statut:"ACTIVE",    nb_diplomes_total:16,  nb_via_microservice:5,   nb_via_upload:11,  nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-05" },
];

export const MOCK_STUDENTS = [
  { etudiant_id:"E001", nom:"Trabelsi",  prenom:"Mehdi",   email:"mehdi.trabelsi@esprit.tn",   numero_etudiant:"ETU-2024-001", nb_diplomes_total:2, nb_confirmes:2, nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-10" },
  { etudiant_id:"E002", nom:"Maatoug",   prenom:"Sana",    email:"sana.maatoug@utm.tn",         numero_etudiant:"ETU-2023-041", nb_diplomes_total:1, nb_confirmes:1, nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-10" },
  { etudiant_id:"E003", nom:"Ben Amara", prenom:"Yassine", email:"yassine.benamara@insat.tn",   numero_etudiant:"ETU-2024-012", nb_diplomes_total:1, nb_confirmes:0, nb_pending:1, nb_revoques:0, derniere_emission:"2026-03-09" },
  { etudiant_id:"E004", nom:"Cherni",    prenom:"Rim",     email:"rim.cherni@esprit.tn",        numero_etudiant:"ETU-2024-007", nb_diplomes_total:3, nb_confirmes:2, nb_pending:1, nb_revoques:0, derniere_emission:"2026-03-09" },
  { etudiant_id:"E005", nom:"Khelifi",   prenom:"Omar",    email:"omar.khelifi@enit.tn",        numero_etudiant:"ETU-2023-088", nb_diplomes_total:1, nb_confirmes:0, nb_pending:0, nb_revoques:1, derniere_emission:"2026-03-08" },
  { etudiant_id:"E006", nom:"Gharbi",    prenom:"Amira",   email:"amira.gharbi@esprit.tn",      numero_etudiant:"ETU-2024-033", nb_diplomes_total:1, nb_confirmes:1, nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-08" },
  { etudiant_id:"E007", nom:"Ferchichi", prenom:"Rami",    email:"rami.ferchichi@utm.tn",       numero_etudiant:"ETU-2023-099", nb_diplomes_total:2, nb_confirmes:2, nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-07" },
];

export const MOCK_DIPLOMES = [
  { id:847, etudiant:"Mehdi Trabelsi",    titre:"Licence Informatique",    inst:"ESPRIT", statut:"ORIGINAL",           generation_mode:"MICROSERVICE", date:"10/03/2026" },
  { id:846, etudiant:"Sana Maatoug",      titre:"Master Finance",          inst:"UTM",    statut:"ORIGINAL",           generation_mode:"UPLOAD",       date:"10/03/2026" },
  { id:845, etudiant:"Yassine Ben Amara", titre:"Cycle Ingénieur Réseaux", inst:"INSAT",  statut:"PENDING_BLOCKCHAIN", generation_mode:"MICROSERVICE", date:"09/03/2026" },
  { id:844, etudiant:"Rim Cherni",        titre:"Licence Gestion",         inst:"ESPRIT", statut:"ORIGINAL",           generation_mode:"UPLOAD",       date:"09/03/2026" },
  { id:843, etudiant:"Omar Khelifi",      titre:"Master Cybersécurité",    inst:"ENIT",   statut:"REVOQUE",            generation_mode:"UPLOAD",       date:"08/03/2026" },
  { id:842, etudiant:"Amira Gharbi",      titre:"Licence GL",              inst:"ESPRIT", statut:"ORIGINAL",           generation_mode:"MICROSERVICE", date:"08/03/2026" },
  { id:838, etudiant:"Rami Ferchichi",    titre:"Master Data Science",     inst:"UTM",    statut:"MODIFIE",            generation_mode:"UPLOAD",       date:"07/03/2026" },
  { id:833, etudiant:"Leila Ben Salah",   titre:"Licence Finance",         inst:"ISG",    statut:"DUPLIQUE",           generation_mode:"UPLOAD",       date:"06/03/2026" },
];

export const MOCK_RETRY_ALERTS = [
  { id:28, etudiant:"Omar Khelifi",  hash:"e9f3...c812", retry:7, age:"27h", inst:"ENIT",   urgent:true  },
  { id:21, etudiant:"Fatma Riahi",   hash:"a2b1...d409", retry:6, age:"38h", inst:"UTM",    urgent:true  },
  { id:15, etudiant:"Karim Boujnah", hash:"f7c4...e182", retry:5, age:"51h", inst:"ESPRIT", urgent:false },
];

export const MOCK_PENDING_ALL = [
  { id:845, etudiant:"Yassine Ben Amara", hash:"c1e8...0a7f", retry:2, age:"18h", inst:"INSAT"  },
  { id:840, etudiant:"Sami Hamdi",        hash:"d5a4...9b3e", retry:0, age:"2h",  inst:"ESPRIT" },
  { id:836, etudiant:"Nour Souissi",      hash:"b7d2...f490", retry:1, age:"5h",  inst:"UTM"    },
  { id:831, etudiant:"Ons Haddad",        hash:"a3f9...e2c1", retry:3, age:"9h",  inst:"ESPRIT" },
  { id:829, etudiant:"Adem Jerbi",        hash:"f1e2...bc30", retry:4, age:"14h", inst:"ENIT"   },
];

export const MOCK_AUDIT_LOG = [
  { type_operation:"CREATION",     acteur:"admin@esprit.tn",    diplome_id:"#847", timestamp:"il y a 4 min",  inst:"ESPRIT", color:"#00D68F" /* green */ },
  { type_operation:"VERIFICATION", acteur:"rh@altran.com",      diplome_id:"#841", timestamp:"il y a 12 min", inst:"—",      color:"#00C8E0" /* cyan */ },
  { type_operation:"CREATION",     acteur:"admin@utm.tn",       diplome_id:"#840", timestamp:"il y a 31 min", inst:"UTM",    color:"#00D68F" /* green */ },
  { type_operation:"REVOCATION",   acteur:"superadmin@chain.tn",diplome_id:"#823", timestamp:"il y a 2h",     inst:"INSAT",  color:"#FF4757" /* red */ },
  { type_operation:"MODIFICATION", acteur:"admin@esprit.tn",    diplome_id:"#812", timestamp:"il y a 3h",     inst:"ESPRIT", color:"#9B6DFF" /* purple? or blue? originally T.blue=#4A9EFF */ },
  { type_operation:"DUPLICATION",  acteur:"admin@utm.tn",       diplome_id:"#808", timestamp:"il y a 5h",     inst:"UTM",    color:"#9B6DFF" /* purple */ },
  { type_operation:"VERIFICATION", acteur:"drh@telnet.com",     diplome_id:"#805", timestamp:"il y a 6h",     inst:"—",      color:"#00C8E0" /* cyan */ },
];

export const MOCK_VALIDATION_REQUESTS = [
  { entreprise_validation_id:1, entreprise_id:3, nom_entreprise:"Altran Technologies", ms_tenant_id:"altran-tenant-001", microsoft_email_domain:"@altran.com",   status:"EN_ATTENTE", demande_at:"2026-03-10 09:14", traite_par:null,                  motif_refus:null },
  { entreprise_validation_id:2, entreprise_id:4, nom_entreprise:"Telnet Consulting",   ms_tenant_id:"telnet-tenant-002", microsoft_email_domain:"@telnet.com.tn", status:"EN_ATTENTE", demande_at:"2026-03-09 14:30", traite_par:null,                  motif_refus:null },
  { entreprise_validation_id:3, entreprise_id:5, nom_entreprise:"Vermeg Group",        ms_tenant_id:"vermeg-tenant-003", microsoft_email_domain:"@vermeg.com",    status:"EN_ATTENTE", demande_at:"2026-03-08 11:05", traite_par:null,                  motif_refus:null },
  { entreprise_validation_id:4, entreprise_id:1, nom_entreprise:"Sofrecom",            ms_tenant_id:"sofrecom-ten-004",  microsoft_email_domain:"@sofrecom.com",  status:"APPROUVEE",  demande_at:"2026-03-01 08:00", traite_par:"superadmin@chain.tn", motif_refus:null },
  { entreprise_validation_id:5, entreprise_id:2, nom_entreprise:"Wevioo",              ms_tenant_id:"wevioo-tenant-005", microsoft_email_domain:"@wevioo.com",    status:"APPROUVEE",  demande_at:"2026-02-20 10:45", traite_par:"superadmin@chain.tn", motif_refus:null },
  { entreprise_validation_id:6, entreprise_id:6, nom_entreprise:"Inconnue SARL",       ms_tenant_id:"unkn-tenant-006",   microsoft_email_domain:"@inconnue.tn",   status:"REFUSEE",    demande_at:"2026-02-15 16:00", traite_par:"superadmin@chain.tn", motif_refus:"Domaine email non vérifié — entreprise non reconnue" },
];

export const MOCK_ENTREPRISES = [
  { entreprise_id:1, nom:"Sofrecom",            microsoft_tenant_id:"sofrecom-ten-004",  microsoft_email_domain:"@sofrecom.com",  status:"APPROUVEE",  nb_verifications:412, derniere_session:"2026-03-10 11:32", is_valid:true  },
  { entreprise_id:2, nom:"Wevioo",              microsoft_tenant_id:"wevioo-tenant-005", microsoft_email_domain:"@wevioo.com",    status:"APPROUVEE",  nb_verifications:287, derniere_session:"2026-03-10 09:18", is_valid:true  },
  { entreprise_id:3, nom:"Altran Technologies", microsoft_tenant_id:"altran-tenant-001", microsoft_email_domain:"@altran.com",    status:"EN_ATTENTE", nb_verifications:0,   derniere_session:null,               is_valid:false },
  { entreprise_id:4, nom:"Telnet Consulting",   microsoft_tenant_id:"telnet-tenant-002", microsoft_email_domain:"@telnet.com.tn", status:"EN_ATTENTE", nb_verifications:0,   derniere_session:null,               is_valid:false },
  { entreprise_id:5, nom:"Vermeg Group",        microsoft_tenant_id:"vermeg-tenant-003", microsoft_email_domain:"@vermeg.com",    status:"EN_ATTENTE", nb_verifications:0,   derniere_session:null,               is_valid:false },
  { entreprise_id:6, nom:"Inconnue SARL",       microsoft_tenant_id:"unkn-tenant-006",   microsoft_email_domain:"@inconnue.tn",   status:"REFUSEE",    nb_verifications:0,   derniere_session:null,               is_valid:false },
];

export const MOCK_AUTH_SESSIONS = [
  { session_id:1001, entreprise_id:1, nom_entreprise:"Sofrecom", microsoft_email:"drh@sofrecom.com",     tenant_id:"sofrecom-ten-004",  expires_at:"2026-03-10 23:59", is_valid:true  },
  { session_id:1002, entreprise_id:1, nom_entreprise:"Sofrecom", microsoft_email:"rh2@sofrecom.com",     tenant_id:"sofrecom-ten-004",  expires_at:"2026-03-10 21:30", is_valid:true  },
  { session_id:1003, entreprise_id:2, nom_entreprise:"Wevioo",   microsoft_email:"talent@wevioo.com",    tenant_id:"wevioo-tenant-005", expires_at:"2026-03-10 18:00", is_valid:true  },
  { session_id:998,  entreprise_id:2, nom_entreprise:"Wevioo",   microsoft_email:"recruteur@wevioo.com", tenant_id:"wevioo-tenant-005", expires_at:"2026-03-09 20:00", is_valid:false },
];
