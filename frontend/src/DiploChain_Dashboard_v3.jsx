import { useState, useEffect, useCallback, createContext, useContext } from "react";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer,
} from "recharts";
import { SimpleLine } from "./components/Charts";
import PaginatedTable from "./components/PaginatedTable";

// ── Design tokens ─────────────────────────────────────────────────────────────
const T = {
  bg0: "#05101F", bg1: "#091929", bg2: "#0D2035", bg3: "#112640",
  border: "#1A3A5C", borderLight: "#1E4570",
  gold: "#C9A227", goldDim: "#8A6D1A", goldPale: "#F5E6B0",
  cyan: "#00C8E0", green: "#00D68F", red: "#FF4757",
  orange: "#FF8C42", blue: "#4A9EFF", purple: "#9B6DFF",
  text0: "#EEF4FF", text1: "#7A9DBB", text2: "#3A6080",
};

// ── React context ─────────────────────────────────────────────────────────────
// FIX #1 : tout passe par le contexte — plus de variables globales hors App
const DataContext = createContext(null);
function useData() {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useData must be used within DataContext.Provider");
  return ctx;
}

// ── Login ─────────────────────────────────────────────────────────────────────
function Login({ onSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const submit = async e => {
    e.preventDefault();
    try {
      const resp = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      const data = await resp.json();
      onSuccess(data.access_token);
    } catch (ex) {
      setErr(ex.message);
    }
  };
  return (
    <div style={{ minHeight:"100vh", background:T.bg0, display:"flex", alignItems:"center", justifyContent:"center" }}>
      <div style={{ background:T.bg2, border:`1px solid ${T.border}`, borderRadius:14, padding:40, width:320 }}>
        <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:28 }}>
          <div style={{ width:36, height:36, borderRadius:9, background:`linear-gradient(135deg,${T.gold},${T.goldDim})`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:18, fontWeight:900, color:T.bg0 }}>◈</div>
          <div>
            <div style={{ fontSize:16, fontWeight:900, color:T.text0 }}>DiploChain</div>
            <div style={{ fontSize:9, color:T.goldDim, letterSpacing:"0.1em", textTransform:"uppercase" }}>Super Admin · v6</div>
          </div>
        </div>
        {err && <div style={{ color:T.red, fontSize:12, marginBottom:12, padding:"8px 10px", background:`${T.red}15`, borderRadius:6 }}>{err}</div>}
        <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
          <input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}
            style={{ padding:"9px 12px", borderRadius:7, border:`1px solid ${T.border}`, background:T.bg3, color:T.text0, fontSize:13, outline:"none" }} />
          <input type="password" placeholder="Mot de passe" value={password} onChange={e=>setPassword(e.target.value)}
            style={{ padding:"9px 12px", borderRadius:7, border:`1px solid ${T.border}`, background:T.bg3, color:T.text0, fontSize:13, outline:"none" }} />
          <button onClick={submit}
            style={{ padding:"10px", borderRadius:7, background:`linear-gradient(135deg,${T.gold},${T.goldDim})`, color:T.bg0, fontWeight:800, cursor:"pointer", border:"none", fontSize:13, marginTop:4 }}>
            Se connecter
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Données mock ──────────────────────────────────────────────────────────────
const MOCK_METRICS_TODAY = {
  metric_date: "2026-03-11",
  nb_diplomes_emis: 847, nb_diplomes_microservice: 235, nb_diplomes_upload: 612,
  nb_nouveaux_etudiants: 142, nb_institutions_actives: 7,
  nb_diplomes_confirmes: 801, nb_diplomes_pending: 23, nb_diplomes_revoques: 23,
  nb_verifications: 2341, updated_at: "2026-03-11T12:00:00",
};
const MOCK_METRICS_DAILY = [
  { mois:"Sep", nb_diplomes_emis:62,  nb_diplomes_confirmes:59,  nb_verifications:180 },
  { mois:"Oct", nb_diplomes_emis:88,  nb_diplomes_confirmes:84,  nb_verifications:241 },
  { mois:"Nov", nb_diplomes_emis:74,  nb_diplomes_confirmes:71,  nb_verifications:198 },
  { mois:"Déc", nb_diplomes_emis:43,  nb_diplomes_confirmes:41,  nb_verifications:112 },
  { mois:"Jan", nb_diplomes_emis:105, nb_diplomes_confirmes:98,  nb_verifications:312 },
  { mois:"Fév", nb_diplomes_emis:127, nb_diplomes_confirmes:120, nb_verifications:387 },
  { mois:"Mar", nb_diplomes_emis:156, nb_diplomes_confirmes:148, nb_verifications:451 },
];
const STATUTS_PIE = [
  { name:"ORIGINAL",           value:801, color:T.green  },
  { name:"PENDING_BLOCKCHAIN", value:23,  color:T.orange },
  { name:"REVOQUE",            value:23,  color:T.red    },
  { name:"MODIFIE",            value:6,   color:T.blue   },
  { name:"DUPLIQUE",           value:3,   color:T.purple },
];
const MODE_PIE = [
  { name:"UPLOAD",       value:612, color:T.gold },
  { name:"MICROSERVICE", value:235, color:T.cyan },
];
const MOCK_INSTITUTIONS = [
  { institution_id:1, nom:"ESPRIT School of Engineering", code:"ESP", statut:"ACTIVE",    nb_diplomes_total:312, nb_via_microservice:180, nb_via_upload:132, nb_pending:8, nb_revoques:4, derniere_emission:"2026-03-10" },
  { institution_id:2, nom:"Université de Tunis El Manar", code:"UTM", statut:"ACTIVE",    nb_diplomes_total:187, nb_via_microservice:90,  nb_via_upload:97,  nb_pending:5, nb_revoques:3, derniere_emission:"2026-03-09" },
  { institution_id:3, nom:"INSAT",                        code:"INS", statut:"ACTIVE",    nb_diplomes_total:143, nb_via_microservice:70,  nb_via_upload:73,  nb_pending:4, nb_revoques:2, derniere_emission:"2026-03-09" },
  { institution_id:4, nom:"ENIT",                         code:"ENI", statut:"ACTIVE",    nb_diplomes_total:98,  nb_via_microservice:40,  nb_via_upload:58,  nb_pending:3, nb_revoques:1, derniere_emission:"2026-03-08" },
  { institution_id:5, nom:"Polytechnique Tunis",          code:"EPT", statut:"ACTIVE",    nb_diplomes_total:67,  nb_via_microservice:30,  nb_via_upload:37,  nb_pending:2, nb_revoques:0, derniere_emission:"2026-03-07" },
  { institution_id:6, nom:"ISG Tunis",                    code:"ISG", statut:"SUSPENDUE", nb_diplomes_total:24,  nb_via_microservice:10,  nb_via_upload:14,  nb_pending:1, nb_revoques:1, derniere_emission:"2026-02-20" },
  { institution_id:7, nom:"ISET Charguia",                code:"IST", statut:"ACTIVE",    nb_diplomes_total:16,  nb_via_microservice:5,   nb_via_upload:11,  nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-05" },
];
const MOCK_STUDENTS = [
  { etudiant_id:"E001", nom:"Trabelsi",  prenom:"Mehdi",   email:"mehdi.trabelsi@esprit.tn",   numero_etudiant:"ETU-2024-001", nb_diplomes_total:2, nb_confirmes:2, nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-10" },
  { etudiant_id:"E002", nom:"Maatoug",   prenom:"Sana",    email:"sana.maatoug@utm.tn",         numero_etudiant:"ETU-2023-041", nb_diplomes_total:1, nb_confirmes:1, nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-10" },
  { etudiant_id:"E003", nom:"Ben Amara", prenom:"Yassine", email:"yassine.benamara@insat.tn",   numero_etudiant:"ETU-2024-012", nb_diplomes_total:1, nb_confirmes:0, nb_pending:1, nb_revoques:0, derniere_emission:"2026-03-09" },
  { etudiant_id:"E004", nom:"Cherni",    prenom:"Rim",     email:"rim.cherni@esprit.tn",        numero_etudiant:"ETU-2024-007", nb_diplomes_total:3, nb_confirmes:2, nb_pending:1, nb_revoques:0, derniere_emission:"2026-03-09" },
  { etudiant_id:"E005", nom:"Khelifi",   prenom:"Omar",    email:"omar.khelifi@enit.tn",        numero_etudiant:"ETU-2023-088", nb_diplomes_total:1, nb_confirmes:0, nb_pending:0, nb_revoques:1, derniere_emission:"2026-03-08" },
  { etudiant_id:"E006", nom:"Gharbi",    prenom:"Amira",   email:"amira.gharbi@esprit.tn",      numero_etudiant:"ETU-2024-033", nb_diplomes_total:1, nb_confirmes:1, nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-08" },
  { etudiant_id:"E007", nom:"Ferchichi", prenom:"Rami",    email:"rami.ferchichi@utm.tn",       numero_etudiant:"ETU-2023-099", nb_diplomes_total:2, nb_confirmes:2, nb_pending:0, nb_revoques:0, derniere_emission:"2026-03-07" },
];
const MOCK_DIPLOMES = [
  { id:847, etudiant:"Mehdi Trabelsi",    titre:"Licence Informatique",    inst:"ESPRIT", statut:"ORIGINAL",           generation_mode:"MICROSERVICE", date:"10/03/2026" },
  { id:846, etudiant:"Sana Maatoug",      titre:"Master Finance",          inst:"UTM",    statut:"ORIGINAL",           generation_mode:"UPLOAD",       date:"10/03/2026" },
  { id:845, etudiant:"Yassine Ben Amara", titre:"Cycle Ingénieur Réseaux", inst:"INSAT",  statut:"PENDING_BLOCKCHAIN", generation_mode:"MICROSERVICE", date:"09/03/2026" },
  { id:844, etudiant:"Rim Cherni",        titre:"Licence Gestion",         inst:"ESPRIT", statut:"ORIGINAL",           generation_mode:"UPLOAD",       date:"09/03/2026" },
  { id:843, etudiant:"Omar Khelifi",      titre:"Master Cybersécurité",    inst:"ENIT",   statut:"REVOQUE",            generation_mode:"UPLOAD",       date:"08/03/2026" },
  { id:842, etudiant:"Amira Gharbi",      titre:"Licence GL",              inst:"ESPRIT", statut:"ORIGINAL",           generation_mode:"MICROSERVICE", date:"08/03/2026" },
  { id:838, etudiant:"Rami Ferchichi",    titre:"Master Data Science",     inst:"UTM",    statut:"MODIFIE",            generation_mode:"UPLOAD",       date:"07/03/2026" },
  { id:833, etudiant:"Leila Ben Salah",   titre:"Licence Finance",         inst:"ISG",    statut:"DUPLIQUE",           generation_mode:"UPLOAD",       date:"06/03/2026" },
];
const MOCK_RETRY_ALERTS = [
  { id:28, etudiant:"Omar Khelifi",  hash:"e9f3...c812", retry:7, age:"27h", inst:"ENIT",   urgent:true  },
  { id:21, etudiant:"Fatma Riahi",   hash:"a2b1...d409", retry:6, age:"38h", inst:"UTM",    urgent:true  },
  { id:15, etudiant:"Karim Boujnah", hash:"f7c4...e182", retry:5, age:"51h", inst:"ESPRIT", urgent:false },
];
const MOCK_PENDING_ALL = [
  { id:845, etudiant:"Yassine Ben Amara", hash:"c1e8...0a7f", retry:2, age:"18h", inst:"INSAT"  },
  { id:840, etudiant:"Sami Hamdi",        hash:"d5a4...9b3e", retry:0, age:"2h",  inst:"ESPRIT" },
  { id:836, etudiant:"Nour Souissi",      hash:"b7d2...f490", retry:1, age:"5h",  inst:"UTM"    },
  { id:831, etudiant:"Ons Haddad",        hash:"a3f9...e2c1", retry:3, age:"9h",  inst:"ESPRIT" },
  { id:829, etudiant:"Adem Jerbi",        hash:"f1e2...bc30", retry:4, age:"14h", inst:"ENIT"   },
];
const MOCK_AUDIT_LOG = [
  { type_operation:"CREATION",     acteur:"admin@esprit.tn",    diplome_id:"#847", timestamp:"il y a 4 min",  inst:"ESPRIT", color:T.green  },
  { type_operation:"VERIFICATION", acteur:"rh@altran.com",      diplome_id:"#841", timestamp:"il y a 12 min", inst:"—",      color:T.cyan   },
  { type_operation:"CREATION",     acteur:"admin@utm.tn",       diplome_id:"#840", timestamp:"il y a 31 min", inst:"UTM",    color:T.green  },
  { type_operation:"REVOCATION",   acteur:"superadmin@chain.tn",diplome_id:"#823", timestamp:"il y a 2h",     inst:"INSAT",  color:T.red    },
  { type_operation:"MODIFICATION", acteur:"admin@esprit.tn",    diplome_id:"#812", timestamp:"il y a 3h",     inst:"ESPRIT", color:T.blue   },
  { type_operation:"DUPLICATION",  acteur:"admin@utm.tn",       diplome_id:"#808", timestamp:"il y a 5h",     inst:"UTM",    color:T.purple },
  { type_operation:"VERIFICATION", acteur:"drh@telnet.com",     diplome_id:"#805", timestamp:"il y a 6h",     inst:"—",      color:T.cyan   },
];
const MOCK_VALIDATION_REQUESTS = [
  { entreprise_validation_id:1, entreprise_id:3, nom_entreprise:"Altran Technologies", ms_tenant_id:"altran-tenant-001", microsoft_email_domain:"@altran.com",   status:"EN_ATTENTE", demande_at:"2026-03-10 09:14", traite_par:null,                  motif_refus:null },
  { entreprise_validation_id:2, entreprise_id:4, nom_entreprise:"Telnet Consulting",   ms_tenant_id:"telnet-tenant-002", microsoft_email_domain:"@telnet.com.tn", status:"EN_ATTENTE", demande_at:"2026-03-09 14:30", traite_par:null,                  motif_refus:null },
  { entreprise_validation_id:3, entreprise_id:5, nom_entreprise:"Vermeg Group",        ms_tenant_id:"vermeg-tenant-003", microsoft_email_domain:"@vermeg.com",    status:"EN_ATTENTE", demande_at:"2026-03-08 11:05", traite_par:null,                  motif_refus:null },
  { entreprise_validation_id:4, entreprise_id:1, nom_entreprise:"Sofrecom",            ms_tenant_id:"sofrecom-ten-004",  microsoft_email_domain:"@sofrecom.com",  status:"APPROUVEE",  demande_at:"2026-03-01 08:00", traite_par:"superadmin@chain.tn", motif_refus:null },
  { entreprise_validation_id:5, entreprise_id:2, nom_entreprise:"Wevioo",              ms_tenant_id:"wevioo-tenant-005", microsoft_email_domain:"@wevioo.com",    status:"APPROUVEE",  demande_at:"2026-02-20 10:45", traite_par:"superadmin@chain.tn", motif_refus:null },
  { entreprise_validation_id:6, entreprise_id:6, nom_entreprise:"Inconnue SARL",       ms_tenant_id:"unkn-tenant-006",   microsoft_email_domain:"@inconnue.tn",   status:"REFUSEE",    demande_at:"2026-02-15 16:00", traite_par:"superadmin@chain.tn", motif_refus:"Domaine email non vérifié — entreprise non reconnue" },
];
const MOCK_ENTREPRISES = [
  { entreprise_id:1, nom:"Sofrecom",            microsoft_tenant_id:"sofrecom-ten-004",  microsoft_email_domain:"@sofrecom.com",  status:"APPROUVEE",  nb_verifications:412, derniere_session:"2026-03-10 11:32", is_valid:true  },
  { entreprise_id:2, nom:"Wevioo",              microsoft_tenant_id:"wevioo-tenant-005", microsoft_email_domain:"@wevioo.com",    status:"APPROUVEE",  nb_verifications:287, derniere_session:"2026-03-10 09:18", is_valid:true  },
  { entreprise_id:3, nom:"Altran Technologies", microsoft_tenant_id:"altran-tenant-001", microsoft_email_domain:"@altran.com",    status:"EN_ATTENTE", nb_verifications:0,   derniere_session:null,               is_valid:false },
  { entreprise_id:4, nom:"Telnet Consulting",   microsoft_tenant_id:"telnet-tenant-002", microsoft_email_domain:"@telnet.com.tn", status:"EN_ATTENTE", nb_verifications:0,   derniere_session:null,               is_valid:false },
  { entreprise_id:5, nom:"Vermeg Group",        microsoft_tenant_id:"vermeg-tenant-003", microsoft_email_domain:"@vermeg.com",    status:"EN_ATTENTE", nb_verifications:0,   derniere_session:null,               is_valid:false },
  { entreprise_id:6, nom:"Inconnue SARL",       microsoft_tenant_id:"unkn-tenant-006",   microsoft_email_domain:"@inconnue.tn",   status:"REFUSEE",    nb_verifications:0,   derniere_session:null,               is_valid:false },
];
const MOCK_AUTH_SESSIONS = [
  { session_id:1001, entreprise_id:1, nom_entreprise:"Sofrecom", microsoft_email:"drh@sofrecom.com",     tenant_id:"sofrecom-ten-004",  expires_at:"2026-03-10 23:59", is_valid:true  },
  { session_id:1002, entreprise_id:1, nom_entreprise:"Sofrecom", microsoft_email:"rh2@sofrecom.com",     tenant_id:"sofrecom-ten-004",  expires_at:"2026-03-10 21:30", is_valid:true  },
  { session_id:1003, entreprise_id:2, nom_entreprise:"Wevioo",   microsoft_email:"talent@wevioo.com",    tenant_id:"wevioo-tenant-005", expires_at:"2026-03-10 18:00", is_valid:true  },
  { session_id:998,  entreprise_id:2, nom_entreprise:"Wevioo",   microsoft_email:"recruteur@wevioo.com", tenant_id:"wevioo-tenant-005", expires_at:"2026-03-09 20:00", is_valid:false },
];

// ── Normaliseurs API → UI ─────────────────────────────────────────────────────
// Mappent les champs du backend (snake_case, noms variables) vers la structure
// attendue par les composants UI. Tolèrent les champs manquants avec des valeurs
// par défaut pour éviter les crashes.

const OP_COLORS = {
  CREATION:     T.green,
  VERIFICATION: T.cyan,
  REVOCATION:   T.red,
  MODIFICATION: T.blue,
  DUPLICATION:  T.purple,
};

function normalizeDiplome(d) {
  // Le backend retourne le modèle DiplomeResponse (SQLAlchemy)
  // Champs possibles : id_diplome/id, nom+prenom/etudiant, titre_diplome/titre,
  //                    nom_institution/inst, statut, generation_mode, created_at/date
  return {
    id:              d.id_diplome ?? d.id ?? d.diplome_id ?? "—",
    etudiant:        d.etudiant
                       ?? (d.nom && d.prenom ? `${d.prenom} ${d.nom}` : null)
                       ?? d.nom_etudiant
                       ?? "—",
    titre:           d.titre_diplome ?? d.titre ?? d.libelle ?? "—",
    inst:            d.nom_institution ?? d.institution ?? d.inst ?? "—",
    statut:          d.statut ?? "—",
    generation_mode: d.generation_mode ?? "UPLOAD",
    date:            d.created_at
                       ? new Date(d.created_at).toLocaleDateString("fr-FR")
                       : d.date ?? "—",
  };
}

function normalizeAuditEntry(e) {
  // historique_operations : type_operation, acteur (ou user_email), diplome_id, timestamp
  const op = e.type_operation ?? e.operation ?? "VERIFICATION";
  return {
    type_operation: op,
    acteur:         e.acteur ?? e.user_email ?? e.performed_by ?? "—",
    diplome_id:     e.diplome_id ? `#${e.diplome_id}` : (e.id_diplome ? `#${e.id_diplome}` : "—"),
    timestamp:      e.timestamp
                      ? new Date(e.timestamp).toLocaleString("fr-FR")
                      : e.created_at
                        ? new Date(e.created_at).toLocaleString("fr-FR")
                        : "—",
    inst:           e.institution ?? e.inst ?? "—",
    color:          OP_COLORS[op] ?? T.text1,
  };
}

function normalizeRetryAlert(d) {
  // diplome en PENDING_BLOCKCHAIN avec blockchain_retry_count >= 5
  return {
    id:      d.id_diplome ?? d.id ?? d.diplome_id,
    etudiant:d.etudiant ?? (d.nom && d.prenom ? `${d.prenom} ${d.nom}` : null) ?? d.nom_etudiant ?? "—",
    hash:    d.hash_sha256
               ? `${d.hash_sha256.slice(0,4)}...${d.hash_sha256.slice(-4)}`
               : d.hash ?? "—",
    retry:   d.blockchain_retry_count ?? d.retry_count ?? d.retry ?? 0,
    age:     d.age ?? (d.created_at
               ? `${Math.round((Date.now()-new Date(d.created_at))/3600000)}h`
               : "—"),
    inst:    d.nom_institution ?? d.institution ?? d.inst ?? "—",
    urgent:  (d.blockchain_retry_count ?? d.retry_count ?? d.retry ?? 0) >= 7,
  };
}

function normalizeValidationRequest(r) {
  return {
    entreprise_validation_id: r.entreprise_validation_id ?? r.id,
    entreprise_id:            r.entreprise_id,
    nom_entreprise:           r.nom_entreprise ?? r.nom ?? "—",
    ms_tenant_id:             r.microsoft_tenant_id ?? r.ms_tenant_id ?? "—",
    microsoft_email_domain:   r.microsoft_email_domain ?? "—",
    status:                   r.statut_validation ?? r.status ?? "EN_ATTENTE",
    demande_at:               r.demande_at ?? r.created_at ?? "—",
    traite_par:               r.traite_par ?? null,
    motif_refus:              r.motif_refus ?? null,
  };
}

function normalizeEntreprise(e) {
  return {
    entreprise_id:          e.id_entreprise ?? e.entreprise_id ?? e.id,
    nom:                    e.nom ?? "—",
    microsoft_tenant_id:    e.microsoft_tenant_id ?? e.ms_tenant_id ?? "—",
    microsoft_email_domain: e.microsoft_email_domain ?? "—",
    status:                 e.statut_validation ?? e.status ?? "EN_ATTENTE",
    nb_verifications:       e.nb_verifications ?? 0,
    derniere_session:       e.derniere_session ?? null,
    is_valid:               (e.statut_validation ?? e.status) === "APPROUVEE",
  };
}

function normalizeAuthSession(s) {
  return {
    session_id:       s.id_session ?? s.session_id ?? s.id,
    entreprise_id:    s.entreprise_id,
    nom_entreprise:   s.nom_entreprise ?? "—",
    microsoft_email:  s.microsoft_email ?? s.email ?? "—",
    tenant_id:        s.microsoft_tenant_id ?? s.tenant_id ?? "—",
    expires_at:       s.expires_at
                        ? new Date(s.expires_at).toLocaleString("fr-FR")
                        : "—",
    is_valid:         s.is_valid ?? s.actif ?? false,
  };
}

// Applique un normaliseur à un tableau ou retourne le fallback mock en cas d'erreur
function applyNorm(data, normFn, fallback) {
  if (!Array.isArray(data)) return fallback;
  try { return data.map(normFn); }
  catch { return fallback; }
}

// ── Navigation — FIX #2 : NAV est une fonction, pas une constante module-level
// pour pouvoir accéder aux données dynamiques (badge retry)
function buildNav(retryCount, pendingRequestsCount) {
  return [
    { id:"overview",     icon:"◈", label:"Vue d'ensemble" },
    { id:"diplomes",     icon:"◉", label:"Diplômes" },
    { id:"etudiants",    icon:"◎", label:"Étudiants" },
    { id:"institutions", icon:"◫", label:"Institutions" },
    { id:"entreprises",  icon:"🏢", label:"Entreprises",   badge: pendingRequestsCount },
    { id:"blockchain",   icon:"⬡", label:"Blockchain",    badge: retryCount },
    { id:"audit",        icon:"◷", label:"Audit Log" },
  ];
}

// ── Helpers UI ────────────────────────────────────────────────────────────────
const STATUT_CFG = {
  ORIGINAL:           { label:"ORIGINAL",   bg:"#003322", fg:T.green,  dot:T.green  },
  PENDING_BLOCKCHAIN: { label:"PENDING",    bg:"#2D1800", fg:T.orange, dot:T.orange },
  REVOQUE:            { label:"RÉVOQUÉ",    bg:"#2D0008", fg:T.red,    dot:T.red    },
  MODIFIE:            { label:"MODIFIÉ",    bg:"#001533", fg:T.blue,   dot:T.blue   },
  DUPLIQUE:           { label:"DUPLIQUÉ",   bg:"#1A0033", fg:T.purple, dot:T.purple },
  ACTIVE:             { label:"ACTIVE",     bg:"#003322", fg:T.green,  dot:T.green  },
  SUSPENDUE:          { label:"SUSPENDUE",  bg:"#2D1800", fg:T.orange, dot:T.orange },
  ARCHIVEE:           { label:"ARCHIVÉE",   bg:"#1A1A1A", fg:T.text1,  dot:T.text2  },
  APPROUVEE:          { label:"APPROUVÉE",  bg:"#003322", fg:T.green,  dot:T.green  },
  EN_ATTENTE:         { label:"EN ATTENTE", bg:"#2D1800", fg:T.orange, dot:T.orange },
  REFUSEE:            { label:"REFUSÉE",    bg:"#2D0008", fg:T.red,    dot:T.red    },
};
function Badge({ statut }) {
  const c = STATUT_CFG[statut] || { label:statut, bg:T.bg3, fg:T.text1, dot:T.text2 };
  return (
    <span style={{ display:"inline-flex", alignItems:"center", gap:5, background:c.bg, color:c.fg, padding:"2px 9px", borderRadius:20, fontSize:10, fontWeight:800, letterSpacing:"0.06em", border:`1px solid ${c.fg}30` }}>
      <span style={{ width:5, height:5, borderRadius:"50%", background:c.dot, flexShrink:0 }} />
      {c.label}
    </span>
  );
}
function ModeBadge({ mode }) {
  const isMS = mode === "MICROSERVICE";
  return (
    <span style={{ display:"inline-flex", alignItems:"center", gap:4, background:isMS?`${T.cyan}15`:`${T.gold}15`, color:isMS?T.cyan:T.gold, padding:"1px 8px", borderRadius:4, fontSize:10, fontWeight:700 }}>
      {isMS?"⚙":"↑"} {mode}
    </span>
  );
}
function Panel({ children, style={} }) {
  return <div style={{ background:T.bg2, border:`1px solid ${T.border}`, borderRadius:12, padding:18, ...style }}>{children}</div>;
}
function STitle({ children, right }) {
  return (
    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:14 }}>
      <div style={{ fontSize:11, fontWeight:800, color:T.text1, textTransform:"uppercase", letterSpacing:"0.12em" }}>{children}</div>
      {right}
    </div>
  );
}
const Tip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background:T.bg1, border:`1px solid ${T.border}`, borderRadius:8, padding:"8px 12px", fontSize:12 }}>
      <div style={{ color:T.gold, fontWeight:700, marginBottom:4 }}>{label}</div>
      {payload.map((p,i) => (
        <div key={i} style={{ display:"flex", gap:8, alignItems:"center" }}>
          <span style={{ width:7, height:7, borderRadius:"50%", background:p.color }} />
          <span style={{ color:T.text1 }}>{p.name}:</span>
          <span style={{ color:T.text0, fontWeight:700 }}>{p.value}</span>
        </div>
      ))}
    </div>
  );
};
function Loader({ label="Chargement…" }) {
  return (
    <div style={{ display:"flex", alignItems:"center", justifyContent:"center", gap:10, padding:"40px 0", color:T.text2 }}>
      <div style={{ width:16, height:16, borderRadius:"50%", border:`2px solid ${T.border}`, borderTopColor:T.gold, animation:"spin 0.8s linear infinite" }}/>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <span style={{ fontSize:12 }}>{label}</span>
    </div>
  );
}
function Empty({ label="Aucune donnée" }) {
  return (
    <div style={{ textAlign:"center", padding:"36px 0", color:T.text2, fontSize:12 }}>
      <div style={{ fontSize:24, marginBottom:8 }}>◌</div>{label}
    </div>
  );
}
function KpiCard({ icon, label, value, sub, accent, delta, warn }) {
  return (
    <div style={{
      background:`linear-gradient(145deg,${T.bg2},${T.bg3})`,
      border:`1px solid ${warn?accent+"60":T.border}`,
      borderRadius:12, padding:"18px 20px", position:"relative", overflow:"hidden",
      boxShadow:warn?`0 0 18px ${accent}20`:"none", cursor:"default", transition:"transform .15s, box-shadow .15s",
    }}
    onMouseEnter={e=>{e.currentTarget.style.transform="translateY(-2px)";e.currentTarget.style.boxShadow=`0 8px 24px ${accent}20`;}}
    onMouseLeave={e=>{e.currentTarget.style.transform="";e.currentTarget.style.boxShadow=warn?`0 0 18px ${accent}20`:"";}}
    >
      <div style={{ position:"absolute", top:-16, right:-16, width:70, height:70, borderRadius:"50%", background:`${accent}15`, pointerEvents:"none" }} />
      <div style={{ fontSize:20, marginBottom:8, color:accent }}>{icon}</div>
      <div style={{ fontSize:26, fontWeight:900, color:T.text0, letterSpacing:"-0.02em", lineHeight:1 }}>
        {typeof value==="number"?value.toLocaleString("fr-FR"):value}
      </div>
      <div style={{ fontSize:11, color:T.text1, marginTop:5 }}>{label}</div>
      {(sub||delta!==undefined)&&(
        <div style={{ display:"flex", alignItems:"center", gap:6, marginTop:6 }}>
          {delta!==undefined&&<span style={{ fontSize:10, fontWeight:800, color:delta>=0?T.green:T.red }}>{delta>=0?"▲":"▼"} {Math.abs(delta)}%</span>}
          {sub&&<span style={{ fontSize:10, color:T.text2 }}>{sub}</span>}
        </div>
      )}
    </div>
  );
}

// ── Pages ─────────────────────────────────────────────────────────────────────

// FIX #3 : Overview lit toutes ses données depuis le contexte
function Overview({ setPage }) {
  const { metricsToday, metricsDaily, retryAlertsData, auditLogData } = useData();
  const taux = metricsToday.nb_diplomes_confirmes && metricsToday.nb_diplomes_pending != null
    ? Math.round(metricsToday.nb_diplomes_confirmes / (metricsToday.nb_diplomes_confirmes + metricsToday.nb_diplomes_pending) * 100)
    : 0;

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:20 }}>
      {retryAlertsData.length > 0 && (
        <div onClick={()=>setPage("blockchain")} style={{
          background:`linear-gradient(135deg,#1F0A00,${T.bg2})`, border:`1px solid ${T.red}50`,
          borderRadius:10, padding:"12px 18px", cursor:"pointer",
          display:"flex", alignItems:"center", gap:12, transition:"border-color .2s",
        }}
        onMouseEnter={e=>e.currentTarget.style.borderColor=T.red+"90"}
        onMouseLeave={e=>e.currentTarget.style.borderColor=T.red+"50"}
        >
          <span style={{ fontSize:18 }}>🔴</span>
          <div>
            <span style={{ color:T.red, fontWeight:800, fontSize:13 }}>{retryAlertsData.length} alerte(s) Retry Worker</span>
            <span style={{ color:T.text1, fontSize:12, marginLeft:8 }}>— diplômes avec blockchain_retry_count ≥ 5</span>
          </div>
          <span style={{ marginLeft:"auto", color:T.text2, fontSize:12 }}>Voir →</span>
        </div>
      )}

      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:12 }}>
        <KpiCard icon="🎓" label="Diplômes émis"           value={metricsToday.nb_diplomes_emis}        accent={T.gold}   delta={12} />
        <KpiCard icon="✅" label="ORIGINAL (confirmés)"    value={metricsToday.nb_diplomes_confirmes}   accent={T.green}  delta={10} />
        <KpiCard icon="⛓"  label="Taux confirmation Fabric" value={`${taux}%`}                         accent={T.cyan}   sub="ORIGINAL/(ORIGINAL+PENDING)" />
        <KpiCard icon="⏳" label="PENDING_BLOCKCHAIN"      value={metricsToday.nb_diplomes_pending}     accent={T.orange} warn={metricsToday.nb_diplomes_pending>15} sub="Retry Worker actif" />
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:12 }}>
        <KpiCard icon="🔍" label="Vérifications QR"        value={metricsToday.nb_verifications}        accent={T.cyan}   delta={8} />
        <KpiCard icon="🏛️" label="Institutions actives"   value={metricsToday.nb_institutions_actives} accent={T.blue} />
        <KpiCard icon="⚙️" label="Via Microservice PDF"    value={metricsToday.nb_diplomes_microservice} accent={T.cyan}  sub="MICROSERVICE" />
        <KpiCard icon="📤" label="Via Upload direct"       value={metricsToday.nb_diplomes_upload}      accent={T.gold}   sub="UPLOAD" />
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"2fr 1fr 1fr", gap:14 }}>
        <Panel>
          <STitle right={<span style={{ fontSize:10, color:T.text2 }}>GET /admin/metrics/daily</span>}>Évolution mensuelle</STitle>
          <ResponsiveContainer width="100%" height={190}>
            <AreaChart data={metricsDaily} margin={{ top:5, right:5, bottom:0, left:-22 }}>
              <defs>
                <linearGradient id="gE" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={T.gold} stopOpacity={0.3}/><stop offset="95%" stopColor={T.gold} stopOpacity={0}/></linearGradient>
                <linearGradient id="gO" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={T.green} stopOpacity={0.3}/><stop offset="95%" stopColor={T.green} stopOpacity={0}/></linearGradient>
              </defs>
              <XAxis dataKey="mois" tick={{ fill:T.text2, fontSize:11 }} axisLine={false} tickLine={false}/>
              <YAxis tick={{ fill:T.text2, fontSize:11 }} axisLine={false} tickLine={false}/>
              <Tooltip content={<Tip/>}/>
              <Area type="monotone" dataKey="nb_diplomes_emis"      name="Émis"     stroke={T.gold}  fill="url(#gE)" strokeWidth={2} dot={false}/>
              <Area type="monotone" dataKey="nb_diplomes_confirmes" name="ORIGINAL" stroke={T.green} fill="url(#gO)" strokeWidth={2} dot={false}/>
            </AreaChart>
          </ResponsiveContainer>
        </Panel>
        <Panel>
          <STitle>Statuts diplômes</STitle>
          <ResponsiveContainer width="100%" height={130}>
            <PieChart><Pie data={STATUTS_PIE} cx="50%" cy="50%" innerRadius={38} outerRadius={60} paddingAngle={2} dataKey="value" stroke="none">
              {STATUTS_PIE.map((e,i)=><Cell key={i} fill={e.color} opacity={0.9}/>)}
            </Pie><Tooltip content={<Tip/>}/></PieChart>
          </ResponsiveContainer>
          <div style={{ display:"flex", flexDirection:"column", gap:4, marginTop:4 }}>
            {STATUTS_PIE.map((e,i)=>(
              <div key={i} style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                <div style={{ display:"flex", alignItems:"center", gap:5 }}>
                  <span style={{ width:7, height:7, borderRadius:"50%", background:e.color }}/>
                  <span style={{ fontSize:10, color:T.text1, fontFamily:"monospace" }}>{e.name}</span>
                </div>
                <span style={{ fontSize:11, color:T.text0, fontWeight:700 }}>{e.value}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel>
          <STitle>generation_mode</STitle>
          <ResponsiveContainer width="100%" height={130}>
            <PieChart><Pie data={MODE_PIE} cx="50%" cy="50%" innerRadius={38} outerRadius={60} paddingAngle={3} dataKey="value" stroke="none">
              {MODE_PIE.map((e,i)=><Cell key={i} fill={e.color} opacity={0.9}/>)}
            </Pie><Tooltip content={<Tip/>}/></PieChart>
          </ResponsiveContainer>
          <div style={{ display:"flex", flexDirection:"column", gap:6, marginTop:8 }}>
            {MODE_PIE.map((e,i)=>(
              <div key={i} style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                <div style={{ display:"flex", alignItems:"center", gap:5 }}>
                  <span style={{ width:7, height:7, borderRadius:"50%", background:e.color }}/>
                  <span style={{ fontSize:10, color:T.text1, fontFamily:"monospace" }}>{e.name}</span>
                </div>
                <span style={{ fontSize:11, color:T.text0, fontWeight:700 }}>{e.value}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:14 }}>
        <Panel>
          <STitle right={<span style={{ fontSize:10, color:T.text2 }}>UC-SA-07 — sort: nb_diplomes_total DESC</span>}>Classement institutions</STitle>
          <ResponsiveContainer width="100%" height={155}>
            <BarChart data={MOCK_INSTITUTIONS.slice(0,5).map(i=>({ code:i.code, value:i.nb_diplomes_total }))} margin={{ top:5, right:5, bottom:0, left:-25 }}>
              <XAxis dataKey="code" tick={{ fill:T.text2, fontSize:11 }} axisLine={false} tickLine={false}/>
              <YAxis tick={{ fill:T.text2, fontSize:11 }} axisLine={false} tickLine={false}/>
              <Tooltip content={<Tip/>}/>
              <Bar dataKey="value" name="Diplômes" fill={T.gold} radius={[4,4,0,0]} maxBarSize={32}/>
            </BarChart>
          </ResponsiveContainer>
        </Panel>
        <Panel>
          <STitle right={<span style={{ fontSize:10, color:T.text2 }}>historique_operations.timestamp</span>}>Activité récente</STitle>
          {auditLogData.slice(0,6).map((e,i)=>(
            <div key={i} style={{ display:"flex", alignItems:"center", gap:8, padding:"5px 0", borderBottom:i<5?`1px solid ${T.border}30`:"none" }}>
              <span style={{ width:6, height:6, borderRadius:"50%", background:e.color, flexShrink:0, boxShadow:`0 0 5px ${e.color}` }}/>
              <span style={{ fontSize:10, fontWeight:800, color:e.color, width:98, flexShrink:0, fontFamily:"monospace" }}>{e.type_operation}</span>
              <span style={{ fontSize:11, color:T.text1, flex:1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{e.acteur}</span>
              <span style={{ fontSize:10, color:T.text2, flexShrink:0 }}>{e.timestamp}</span>
            </div>
          ))}
        </Panel>
      </div>
    </div>
  );
}

function DiplomesPage() {
  const { diplomesData, loading } = useData();
  const [search, setSearch] = useState("");
  const [statutFilter, setStatutFilter] = useState("TOUS");
  const [modeFilter, setModeFilter] = useState("TOUS");
  const filtered = diplomesData.filter(d => {
    const ms = search.toLowerCase();
    return ((d.etudiant||"").toLowerCase().includes(ms)||(d.titre||"").toLowerCase().includes(ms)||String(d.id).includes(ms))
      && (statutFilter==="TOUS"||d.statut===statutFilter)
      && (modeFilter==="TOUS"||d.generation_mode===modeFilter);
  });
  return (
    <Panel>
      <STitle right={<span style={{ fontSize:10, color:T.text2 }}>GET /diplomes/ — {diplomesData.length} diplôme(s)</span>}>Diplômes — {filtered.length} résultat(s)</STitle>
      {loading["diplomes"] ? <Loader label="Chargement des diplômes…"/> : (
      <React.Fragment>
      <div style={{ display:"flex", gap:8, marginBottom:14, flexWrap:"wrap" }}>
        <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Rechercher ID, étudiant, titre…"
          style={{ flex:1, minWidth:200, background:T.bg3, border:`1px solid ${T.border}`, borderRadius:7, padding:"7px 11px", color:T.text0, fontSize:12, outline:"none" }}/>
        <div style={{ display:"flex", gap:6, flexWrap:"wrap" }}>
          {["TOUS","ORIGINAL","PENDING_BLOCKCHAIN","REVOQUE","MODIFIE","DUPLIQUE"].map(s=>(
            <button key={s} onClick={()=>setStatutFilter(s)} style={{ background:statutFilter===s?T.gold:T.bg3, color:statutFilter===s?T.bg0:T.text1, border:`1px solid ${statutFilter===s?T.gold:T.border}`, borderRadius:6, padding:"6px 10px", fontSize:10, cursor:"pointer", fontWeight:800, fontFamily:"monospace", transition:"all .15s" }}>
              {s==="TOUS"?"ALL":s==="PENDING_BLOCKCHAIN"?"PENDING":s}
            </button>
          ))}
        </div>
        <div style={{ display:"flex", gap:6 }}>
          {["TOUS","UPLOAD","MICROSERVICE"].map(m=>(
            <button key={m} onClick={()=>setModeFilter(m)} style={{ background:modeFilter===m?(m==="MICROSERVICE"?T.cyan:T.gold):T.bg3, color:modeFilter===m?T.bg0:T.text1, border:`1px solid ${modeFilter===m?(m==="MICROSERVICE"?T.cyan:T.gold):T.border}`, borderRadius:6, padding:"6px 10px", fontSize:10, cursor:"pointer", fontWeight:700, transition:"all .15s" }}>
              {m}
            </button>
          ))}
        </div>
      </div>
      {/* chart for creation per date */}
      <div style={{ marginBottom:20 }}>
        <h4>Diplômes créés par date</h4>
        <SimpleLine data={Object.entries(filtered.reduce((acc,d)=>{
          const day = d.date || 'unknown'; acc[day] = (acc[day]||0)+1; return acc;
        },{})).map(([date,count])=>({date,count}))} dataKey="count" />
      </div>
      {/* paginated table for diplomas */}
      <PaginatedTable
        columns={[
          { header:'#ID', render:d=>`#${d.id}` },
          { header:'Étudiant', render:d=>d.etudiant },
          { header:'Titre', render:d=>d.titre },
          { header:'Institution', render:d=>d.inst },
          { header:'Mode', render:d=><ModeBadge mode={d.generation_mode}/> },
          { header:'Statut', render:d=><Badge statut={d.statut}/> },
          { header:'Date', render:d=>d.date },
          { header:'', render:()=>(<button style={{ background:"transparent", border:`1px solid ${T.border}`, color:T.text2, padding:"2px 8px", borderRadius:4, fontSize:10, cursor:"pointer" }}>Voir</button>) }
        ]}
        data={filtered}
        pageSize={25}
        exportFilename="diplomes.csv"
      />
      </React.Fragment>
      )}
    </Panel>
  );
}

function EtudiantsPage() {
  const { studentsData } = useData();
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("nb_diplomes_total");
  const filtered = studentsData
    .filter(e=>{ const ms=search.toLowerCase(); return e.nom.toLowerCase().includes(ms)||e.prenom.toLowerCase().includes(ms)||e.email.toLowerCase().includes(ms)||e.numero_etudiant.toLowerCase().includes(ms); })
    .sort((a,b)=>b[sortBy]-a[sortBy]);
  return (
    <Panel>
      <STitle right={<span style={{ fontSize:10, color:T.text2 }}>GET /admin/students — v_diplomas_per_student</span>}>Étudiants — UC-SA-03</STitle>
      <div style={{ display:"flex", gap:8, marginBottom:14 }}>
        <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Rechercher nom, prénom, email, numéro…"
          style={{ flex:1, background:T.bg3, border:`1px solid ${T.border}`, borderRadius:7, padding:"7px 11px", color:T.text0, fontSize:12, outline:"none" }}/>
        <select value={sortBy} onChange={e=>setSortBy(e.target.value)} style={{ background:T.bg3, border:`1px solid ${T.border}`, color:T.text0, borderRadius:7, padding:"7px 10px", fontSize:11, cursor:"pointer", outline:"none" }}>
          <option value="nb_diplomes_total">Trier : nb_diplomes_total</option>
          <option value="nb_confirmes">Trier : nb_confirmes</option>
          <option value="nb_pending">Trier : nb_pending</option>
        </select>
      </div>
      {/* optional distribution chart */}
      <div style={{ marginBottom:20 }}>
        <h4>Répartition des diplômes par étudiant</h4>
        <SimpleLine data={Object.entries(filtered.reduce((acc,e)=>{
          const tot = e.nb_diplomes_total;
          acc[tot] = (acc[tot]||0)+1; return acc;
        },{})).map(([tot,count])=>({ date:tot, count }))} xKey="date" dataKey="count" stroke={T.blue} />
      </div>
      <PaginatedTable
        columns={[
          { header:'Étudiant', render:e=>`${e.prenom} ${e.nom}` },
          { header:'N° Étudiant', render:e=>e.numero_etudiant },
          { header:'Email', render:e=>e.email },
          { header:'Total', render:e=>e.nb_diplomes_total },
          { header:'ORIGINAL', render:e=>e.nb_confirmes },
          { header:'PENDING', render:e=>e.nb_pending },
          { header:'RÉVOQUÉ', render:e=>e.nb_revoques },
          { header:'Dernière émission', render:e=>e.derniere_emission },
        ]}
        data={filtered}
        pageSize={25}
        exportFilename="etudiants.csv"
      />
    </Panel>
  );
}

function InstitutionsPage() {
  const { institutionsData } = useData();
  const [sortBy, setSortBy] = useState("nb_diplomes_total");
  const sorted = [...institutionsData].sort((a,b)=>b[sortBy]-a[sortBy]);
  return (
    <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
      <Panel>
        <STitle right={
          <div style={{ display:"flex", gap:6, alignItems:"center" }}>
            <span style={{ fontSize:10, color:T.text2 }}>GET /admin/institutions — v_diplomas_per_institution</span>
            <select value={sortBy} onChange={e=>setSortBy(e.target.value)} style={{ background:T.bg3, border:`1px solid ${T.border}`, color:T.text0, borderRadius:5, padding:"4px 8px", fontSize:10, cursor:"pointer", outline:"none" }}>
              <option value="nb_diplomes_total">sort: nb_diplomes_total</option>
              <option value="nb_via_microservice">sort: nb_via_microservice</option>
              <option value="nb_via_upload">sort: nb_via_upload</option>
              <option value="nb_pending">sort: nb_pending</option>
            </select>
          </div>
        }>Institutions — UC-SA-04 / UC-SA-07</STitle>
        <table style={{ width:"100%", borderCollapse:"collapse" }}>
          <thead><tr style={{ borderBottom:`1px solid ${T.border}` }}>
            {["Code","Institution","Statut","Total","Microservice","Upload","Pending","Révoqués","Dernière émission"].map(h=>(
              <th key={h} style={{ padding:"7px 10px", textAlign:"left", fontSize:10, fontWeight:800, color:T.text2, textTransform:"uppercase", letterSpacing:"0.06em" }}>{h}</th>
            ))}
          </tr></thead>
          <tbody>{sorted.map(inst=>{
            const pct=Math.round((inst.nb_diplomes_total-inst.nb_pending-inst.nb_revoques)/Math.max(inst.nb_diplomes_total,1)*100);
            return (
              <tr key={inst.institution_id} onMouseEnter={e=>e.currentTarget.style.background=`${T.bg3}90`} onMouseLeave={e=>e.currentTarget.style.background=""} style={{ borderBottom:`1px solid ${T.border}20`, transition:"background .1s" }}>
                <td style={{ padding:"10px 10px", fontSize:12, color:T.gold, fontWeight:900, fontFamily:"monospace" }}>{inst.code}</td>
                <td style={{ padding:"10px 10px" }}>
                  <div style={{ fontSize:12, color:T.text0, fontWeight:600 }}>{inst.nom}</div>
                  <div style={{ marginTop:4, height:3, width:80, background:T.bg0, borderRadius:2, overflow:"hidden" }}>
                    <div style={{ height:"100%", width:`${pct}%`, background:`linear-gradient(90deg,${T.gold},${T.green})`, borderRadius:2 }}/>
                  </div>
                </td>
                <td style={{ padding:"10px 10px" }}><Badge statut={inst.statut}/></td>
                <td style={{ padding:"10px 10px", fontSize:14, color:T.gold, fontWeight:900, textAlign:"center" }}>{inst.nb_diplomes_total}</td>
                <td style={{ padding:"10px 10px", fontSize:12, color:T.cyan, fontWeight:700, textAlign:"center" }}>{inst.nb_via_microservice}</td>
                <td style={{ padding:"10px 10px", fontSize:12, color:T.gold, fontWeight:700, textAlign:"center" }}>{inst.nb_via_upload}</td>
                <td style={{ padding:"10px 10px", fontSize:12, color:inst.nb_pending>5?T.orange:T.text1, fontWeight:inst.nb_pending>5?800:400, textAlign:"center" }}>{inst.nb_pending}</td>
                <td style={{ padding:"10px 10px", fontSize:12, color:inst.nb_revoques>3?T.red:T.text2, textAlign:"center" }}>{inst.nb_revoques}</td>
                <td style={{ padding:"10px 10px", fontSize:10, color:T.text2 }}>{inst.derniere_emission}</td>
              </tr>
            );
          })}</tbody>
        </table>
      </Panel>
    </div>
  );
}

function BlockchainPage() {
  const { retryAlertsData, pendingData, loading } = useData();
  const [retrying, setRetrying] = useState({});
  const doRetry = id => { setRetrying(r=>({...r,[id]:true})); setTimeout(()=>setRetrying(r=>({...r,[id]:false})),2000); };
  const isLoading = loading["blockchain"];
  return (
    <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:12 }}>
        {[
          { label:"Hyperledger Fabric", sub:"RegisterDiploma() / QueryDiploma()", ok:true,  icon:"⬡" },
          { label:"IPFS Node",          sub:"Publication PDF · CID ancré on-chain",ok:true,  icon:"◎" },
          { label:"Microservice PDF",   sub:"POST /generate-diploma · WeasyPrint", ok:true,  icon:"⚙" },
        ].map(s=>(
          <Panel key={s.label} style={{ display:"flex", alignItems:"center", gap:12 }}>
            <span style={{ fontSize:22, color:s.ok?T.green:T.red }}>{s.icon}</span>
            <div><div style={{ fontSize:12, fontWeight:700, color:T.text0 }}>{s.label}</div><div style={{ fontSize:10, color:T.text2, marginTop:2 }}>{s.sub}</div></div>
            <div style={{ marginLeft:"auto", display:"flex", alignItems:"center", gap:5 }}>
              <span style={{ width:7, height:7, borderRadius:"50%", background:s.ok?T.green:T.red, boxShadow:`0 0 8px ${s.ok?T.green:T.red}` }}/>
              <span style={{ fontSize:10, color:s.ok?T.green:T.red, fontWeight:700 }}>{s.ok?"Actif":"Hors ligne"}</span>
            </div>
          </Panel>
        ))}
      </div>

      <Panel style={{ background:`linear-gradient(135deg,#1A0500,${T.bg2})`, border:`1px solid ${T.red}50` }}>
        <STitle right={<button style={{ background:`${T.red}20`, border:`1px solid ${T.red}50`, color:T.red, padding:"5px 14px", borderRadius:6, fontSize:11, fontWeight:800, cursor:"pointer" }}>Retry All (critiques)</button>}>
          🔴 Alertes — blockchain_retry_count ≥ 5 ({retryAlertsData.length})
        </STitle>
        {isLoading ? <Loader label="Récupération des alertes…"/> : retryAlertsData.length === 0 ? (
          <div style={{ textAlign:"center", padding:"24px 0", color:T.green, fontSize:12 }}>✓ Aucune alerte critique — tous les diplômes sont confirmés</div>
        ) : (
        <table style={{ width:"100%", borderCollapse:"collapse" }}>
          <thead><tr style={{ borderBottom:`1px solid ${T.border}` }}>
            {["#ID","Étudiant","Hash SHA-256","Institution","retry_count","Âge","Action"].map(h=>(
              <th key={h} style={{ padding:"7px 10px", textAlign:"left", fontSize:10, fontWeight:800, color:T.text2, textTransform:"uppercase", letterSpacing:"0.07em" }}>{h}</th>
            ))}
          </tr></thead>
          <tbody>{retryAlertsData.map(d=>(
            <tr key={d.id} onMouseEnter={e=>e.currentTarget.style.background=`${T.bg3}90`} onMouseLeave={e=>e.currentTarget.style.background=""} style={{ borderBottom:`1px solid ${T.border}20`, transition:"background .1s" }}>
              <td style={{ padding:"10px 10px", fontSize:11, color:T.gold, fontWeight:800, fontFamily:"monospace" }}>#{d.id}</td>
              <td style={{ padding:"10px 10px", fontSize:12, color:T.text0, fontWeight:600 }}>{d.etudiant}</td>
              <td style={{ padding:"10px 10px", fontSize:11, color:T.text2, fontFamily:"monospace" }}>{d.hash}</td>
              <td style={{ padding:"10px 10px", fontSize:11, color:T.text1 }}>{d.inst}</td>
              <td style={{ padding:"10px 10px" }}><span style={{ fontSize:14, fontWeight:900, color:T.red }}>{d.retry}</span><span style={{ fontSize:10, color:T.text2 }}> / 10</span></td>
              <td style={{ padding:"10px 10px", fontSize:11, color:T.red, fontWeight:700 }}>{d.age}</td>
              <td style={{ padding:"10px 10px" }}>
                <button onClick={()=>doRetry(d.id)} style={{ background:retrying[d.id]?T.bg3:`${T.red}20`, color:retrying[d.id]?T.text2:T.red, border:`1px solid ${retrying[d.id]?T.border:T.red}50`, borderRadius:6, padding:"4px 12px", fontSize:11, cursor:"pointer", fontWeight:800 }}>
                  {retrying[d.id]?"⟳ …":"Force Retry"}
                </button>
              </td>
            </tr>
          ))}</tbody>
        </table>
        )}
      </Panel>

      <Panel>
        <STitle right={<button style={{ background:`${T.orange}20`, border:`1px solid ${T.orange}50`, color:T.orange, padding:"5px 14px", borderRadius:6, fontSize:11, fontWeight:700, cursor:"pointer" }}>Retry All</button>}>
          ⏳ PENDING_BLOCKCHAIN — Retry Worker actif (retry &lt; 5) — {pendingData.length} diplôme(s)
        </STitle>
        {isLoading ? <Loader label="Récupération des PENDING…"/> : pendingData.length === 0 ? (
          <div style={{ textAlign:"center", padding:"24px 0", color:T.green, fontSize:12 }}>✓ Aucun diplôme en attente</div>
        ) : (
        <table style={{ width:"100%", borderCollapse:"collapse" }}>
          <thead><tr style={{ borderBottom:`1px solid ${T.border}` }}>
            {["#ID","Étudiant","Hash SHA-256","Institution","retry_count","Âge","Action"].map(h=>(
              <th key={h} style={{ padding:"7px 10px", textAlign:"left", fontSize:10, fontWeight:800, color:T.text2, textTransform:"uppercase", letterSpacing:"0.07em" }}>{h}</th>
            ))}
          </tr></thead>
          <tbody>{pendingData.map(d=>(
            <tr key={d.id} onMouseEnter={e=>e.currentTarget.style.background=`${T.bg3}90`} onMouseLeave={e=>e.currentTarget.style.background=""} style={{ borderBottom:`1px solid ${T.border}20`, transition:"background .1s" }}>
              <td style={{ padding:"9px 10px", fontSize:11, color:T.gold, fontWeight:800, fontFamily:"monospace" }}>#{d.id}</td>
              <td style={{ padding:"9px 10px", fontSize:12, color:T.text0, fontWeight:600 }}>{d.etudiant}</td>
              <td style={{ padding:"9px 10px", fontSize:11, color:T.text2, fontFamily:"monospace" }}>{d.hash}</td>
              <td style={{ padding:"9px 10px", fontSize:11, color:T.text1 }}>{d.inst}</td>
              <td style={{ padding:"9px 10px", fontSize:13, color:d.retry>=3?T.orange:T.green, fontWeight:800 }}>{d.retry}</td>
              <td style={{ padding:"9px 10px", fontSize:11, color:T.text2 }}>{d.age}</td>
              <td style={{ padding:"9px 10px" }}>
                <button onClick={()=>doRetry(d.id)} style={{ background:retrying[d.id]?T.bg3:`${T.orange}15`, color:retrying[d.id]?T.text2:T.orange, border:`1px solid ${retrying[d.id]?T.border:T.orange}50`, borderRadius:6, padding:"4px 10px", fontSize:10, cursor:"pointer", fontWeight:700 }}>
                  {retrying[d.id]?"⟳":"Retry"}
                </button>
              </td>
            </tr>
          ))}</tbody>
        </table>
        )}
      </Panel>
    </div>
  );
}

function EntreprisesPage() {
  const { validationRequestsData, entreprisesData, authSessionsData, loading } = useData();
  const isLoading = loading["entreprises"];
  const [activeTab, setActiveTab] = useState("demandes");
  const [processing, setProcessing] = useState({});
  const [showMotif, setShowMotif] = useState(null);
  const [motifText, setMotifText] = useState("");

  const pending  = validationRequestsData.filter(r=>r.status==="EN_ATTENTE");
  const treated  = validationRequestsData.filter(r=>r.status!=="EN_ATTENTE");
  const activeSessions = authSessionsData.filter(s=>s.is_valid);

  const doAction = (id, action) => {
    if (action==="REFUSER") { setShowMotif(id); return; }
    setProcessing(p=>({...p,[id]:action}));
    setTimeout(()=>setProcessing(p=>{const n={...p};delete n[id];return n;}),2000);
  };
  const confirmRefus = id => {
    setProcessing(p=>({...p,[id]:"REFUSER"}));
    setShowMotif(null); setMotifText("");
    setTimeout(()=>setProcessing(p=>{const n={...p};delete n[id];return n;}),2000);
  };

  const TABS = [
    { id:"demandes",    label:"Demandes d'accès",    count:pending.length,                                              color:T.orange },
    { id:"entreprises", label:"Entreprises actives", count:entreprisesData.filter(e=>e.status==="APPROUVEE").length,    color:T.green  },
    { id:"sessions",    label:"Sessions SSO",         count:activeSessions.length,                                      color:T.cyan   },
    { id:"historique",  label:"Historique",           count:treated.length,                                             color:T.text1  },
  ];

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
      {isLoading && <Loader label="Chargement des données entreprises…"/>}
      {!isLoading && pending.length>0&&(
        <Panel style={{ background:`linear-gradient(135deg,#1A1000,${T.bg2})`, border:`1px solid ${T.orange}50` }}>
          <div style={{ display:"flex", alignItems:"center", gap:10 }}>
            <span style={{ fontSize:18 }}>🟠</span>
            <span style={{ color:T.orange, fontWeight:800, fontSize:13 }}>{pending.length} demande(s) d'accès en attente</span>
            <span style={{ color:T.text1, fontSize:12, marginLeft:4 }}>— validation Azure AD requise</span>
          </div>
        </Panel>
      )}
      {!isLoading && <React.Fragment>
      <div style={{ display:"flex", gap:6 }}>
        {TABS.map(tab=>(
          <button key={tab.id} onClick={()=>setActiveTab(tab.id)} style={{ display:"flex", alignItems:"center", gap:7, background:activeTab===tab.id?`${tab.color}18`:T.bg2, border:`1px solid ${activeTab===tab.id?tab.color+"50":T.border}`, color:activeTab===tab.id?tab.color:T.text1, borderRadius:8, padding:"8px 14px", cursor:"pointer", fontSize:12, fontWeight:activeTab===tab.id?800:500, transition:"all .15s" }}>
            {tab.label}
            <span style={{ background:activeTab===tab.id?tab.color:T.bg3, color:activeTab===tab.id?T.bg0:T.text2, borderRadius:10, padding:"1px 7px", fontSize:10, fontWeight:900 }}>{tab.count}</span>
          </button>
        ))}
      </div>

      {activeTab==="demandes"&&(
        <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
          {pending.length===0?(
            <Panel><div style={{ textAlign:"center", padding:"30px 0", color:T.text2 }}>✓ Aucune demande en attente</div></Panel>
          ):pending.map(req=>(
            <Panel key={req.entreprise_validation_id} style={{ border:`1px solid ${T.orange}30`, background:`linear-gradient(135deg,#110D00,${T.bg2})` }}>
              <div style={{ display:"flex", alignItems:"flex-start", gap:16 }}>
                <div style={{ flex:1 }}>
                  <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:8 }}>
                    <div style={{ width:36, height:36, borderRadius:8, background:`${T.orange}20`, border:`1px solid ${T.orange}40`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:16 }}>🏢</div>
                    <div>
                      <div style={{ fontSize:14, fontWeight:800, color:T.text0 }}>{req.nom_entreprise}</div>
                      <div style={{ fontSize:10, color:T.text2, fontFamily:"monospace" }}>entreprise_id: #{req.entreprise_id}</div>
                    </div>
                    <Badge statut="EN_ATTENTE"/>
                  </div>
                  <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"6px 24px" }}>
                    {[{label:"ms_tenant_id",value:req.ms_tenant_id},{label:"microsoft_email_domain",value:req.microsoft_email_domain},{label:"demande_at",value:req.demande_at},{label:"traite_par",value:req.traite_par||"—"}].map(f=>(
                      <div key={f.label}>
                        <div style={{ fontSize:9, color:T.text2, textTransform:"uppercase", letterSpacing:"0.07em", marginBottom:1 }}>{f.label}</div>
                        <div style={{ fontSize:11, color:T.text1, fontFamily:"monospace" }}>{f.value}</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div style={{ display:"flex", flexDirection:"column", gap:8, minWidth:130 }}>
                  <button onClick={()=>doAction(req.entreprise_validation_id,"APPROUVER")} style={{ background:processing[req.entreprise_validation_id]==="APPROUVER"?T.bg3:`${T.green}20`, color:processing[req.entreprise_validation_id]==="APPROUVER"?T.text2:T.green, border:`1px solid ${processing[req.entreprise_validation_id]==="APPROUVER"?T.border:T.green}50`, borderRadius:8, padding:"9px 0", width:"100%", fontSize:12, cursor:"pointer", fontWeight:800, transition:"all .15s" }}>
                    {processing[req.entreprise_validation_id]==="APPROUVER"?"⟳ Traitement…":"✓ Approuver"}
                  </button>
                  <button onClick={()=>doAction(req.entreprise_validation_id,"REFUSER")} style={{ background:processing[req.entreprise_validation_id]==="REFUSER"?T.bg3:`${T.red}15`, color:processing[req.entreprise_validation_id]==="REFUSER"?T.text2:T.red, border:`1px solid ${processing[req.entreprise_validation_id]==="REFUSER"?T.border:T.red}50`, borderRadius:8, padding:"9px 0", width:"100%", fontSize:12, cursor:"pointer", fontWeight:800, transition:"all .15s" }}>
                    {processing[req.entreprise_validation_id]==="REFUSER"?"⟳ Traitement…":"✗ Refuser"}
                  </button>
                </div>
              </div>
              {showMotif===req.entreprise_validation_id&&(
                <div style={{ marginTop:14, padding:"12px 14px", background:`${T.red}10`, border:`1px solid ${T.red}30`, borderRadius:8 }}>
                  <div style={{ fontSize:11, color:T.red, fontWeight:700, marginBottom:6 }}>motif_refus — OBLIGATOIRE (CHECK chk_motif_refus)</div>
                  <textarea value={motifText} onChange={e=>setMotifText(e.target.value)} placeholder="Justification du refus…" rows={3}
                    style={{ width:"100%", background:T.bg3, border:`1px solid ${T.border}`, borderRadius:6, padding:"8px 10px", color:T.text0, fontSize:12, resize:"none", outline:"none", fontFamily:"inherit" }}/>
                  <div style={{ display:"flex", gap:8, marginTop:8, justifyContent:"flex-end" }}>
                    <button onClick={()=>{setShowMotif(null);setMotifText("");}} style={{ background:"transparent", border:`1px solid ${T.border}`, color:T.text1, borderRadius:6, padding:"5px 14px", fontSize:11, cursor:"pointer" }}>Annuler</button>
                    <button onClick={()=>confirmRefus(req.entreprise_validation_id)} disabled={!motifText.trim()} style={{ background:motifText.trim()?`${T.red}20`:"transparent", color:motifText.trim()?T.red:T.text2, border:`1px solid ${motifText.trim()?T.red:T.border}50`, borderRadius:6, padding:"5px 14px", fontSize:11, cursor:motifText.trim()?"pointer":"not-allowed", fontWeight:700 }}>Confirmer</button>
                  </div>
                </div>
              )}
            </Panel>
          ))}
        </div>
      )}

      {activeTab==="entreprises"&&(
        <Panel>
          <STitle right={<span style={{ fontSize:10, color:T.text2 }}>TABLE entreprise — statut_validation ENUM</span>}>Entreprises ({entreprisesData.length})</STitle>
          <PaginatedTable
            columns={[
              { header:'#ID', render:e=>`#${e.entreprise_id}` },
              { header:'Entreprise', render:e=>e.nom },
              { header:'Domaine email', render:e=>e.microsoft_email_domain },
              { header:'Tenant Azure AD', render:e=>e.microsoft_tenant_id },
              { header:'Vérifications', render:e=>e.nb_verifications },
              { header:'Dernière session', render:e=>e.derniere_session||"—" },
              { header:'Statut', render:e=><Badge statut={e.status}/> },
              { header:'', render:()=>(<button style={{ background:"transparent", border:`1px solid ${T.border}`, color:T.text2, padding:"2px 8px", borderRadius:4, fontSize:10, cursor:"pointer" }}>Détails</button>) },
            ]}
            data={entreprisesData}
            pageSize={20}
            exportFilename="entreprises.csv"
          />
        </Panel>
      )}

      {activeTab==="sessions"&&(
        <Panel>
          <STitle right={<span style={{ fontSize:10, color:T.text2 }}>TABLE entreprise_auth_sessions — JWT Azure AD RS256</span>}>Sessions OAuth2 Azure AD</STitle>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:10, marginBottom:16 }}>
            {[
              { label:"Sessions actives",    value:authSessionsData.filter(s=>s.is_valid).length,  color:T.green },
              { label:"Sessions expirées",   value:authSessionsData.filter(s=>!s.is_valid).length, color:T.text2 },
              { label:"Entreprises connectées", value:[...new Set(authSessionsData.filter(s=>s.is_valid).map(s=>s.entreprise_id))].length, color:T.cyan },
            ].map(s=>(
              <div key={s.label} style={{ background:T.bg3, border:`1px solid ${T.border}`, borderRadius:8, padding:"12px 16px" }}>
                <div style={{ fontSize:22, fontWeight:900, color:s.color }}>{s.value}</div>
                <div style={{ fontSize:10, color:T.text1, marginTop:3 }}>{s.label}</div>
              </div>
            ))}
          </div>
          <table style={{ width:"100%", borderCollapse:"collapse" }}>
            <thead><tr style={{ borderBottom:`1px solid ${T.border}` }}>
              {["Session ID","Entreprise","Microsoft email","Tenant ID","Expiration","is_valid"].map(h=>(
                <th key={h} style={{ padding:"7px 10px", textAlign:"left", fontSize:10, fontWeight:800, color:T.text2, textTransform:"uppercase", letterSpacing:"0.06em" }}>{h}</th>
              ))}
            </tr></thead>
            <tbody>{authSessionsData.map(s=>(
              <tr key={s.session_id} onMouseEnter={e=>e.currentTarget.style.background=`${T.bg3}90`} onMouseLeave={e=>e.currentTarget.style.background=""} style={{ borderBottom:`1px solid ${T.border}20`, transition:"background .1s", opacity:s.is_valid?1:0.5 }}>
                <td style={{ padding:"9px 10px", fontSize:11, color:T.gold, fontFamily:"monospace", fontWeight:700 }}>#{s.session_id}</td>
                <td style={{ padding:"9px 10px", fontSize:12, color:T.text0, fontWeight:600 }}>{s.nom_entreprise}</td>
                <td style={{ padding:"9px 10px", fontSize:11, color:T.text1 }}>{s.microsoft_email}</td>
                <td style={{ padding:"9px 10px", fontSize:10, color:T.text2, fontFamily:"monospace" }}>{s.tenant_id}</td>
                <td style={{ padding:"9px 10px", fontSize:10, color:s.is_valid?T.text1:T.red }}>{s.expires_at}</td>
                <td style={{ padding:"9px 10px" }}><span style={{ fontSize:10, fontWeight:800, color:s.is_valid?T.green:T.red, background:s.is_valid?`${T.green}15`:`${T.red}15`, padding:"2px 8px", borderRadius:4, fontFamily:"monospace" }}>{s.is_valid?"true":"false"}</span></td>
              </tr>
            ))}</tbody>
          </table>
        </Panel>
      )}

      {activeTab==="historique"&&(
        <Panel>
          <STitle right={<span style={{ fontSize:10, color:T.text2 }}>entreprise_validation_requests — traitées</span>}>Demandes traitées</STitle>
          <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
            {treated.map(req=>(
              <div key={req.entreprise_validation_id} style={{ background:T.bg3, border:`1px solid ${req.status==="APPROUVEE"?T.green+"30":T.red+"30"}`, borderRadius:10, padding:"14px 16px" }}>
                <div style={{ display:"flex", alignItems:"center", gap:10 }}>
                  <span style={{ fontSize:16 }}>{req.status==="APPROUVEE"?"✅":"❌"}</span>
                  <div style={{ flex:1 }}>
                    <div style={{ fontSize:13, fontWeight:700, color:T.text0 }}>{req.nom_entreprise}</div>
                    <div style={{ fontSize:10, color:T.text2, marginTop:2, fontFamily:"monospace" }}>{req.microsoft_email_domain} · {req.ms_tenant_id}</div>
                  </div>
                  <Badge statut={req.status}/>
                  <div style={{ textAlign:"right" }}>
                    <div style={{ fontSize:10, color:T.text2 }}>Demandé : {req.demande_at}</div>
                    <div style={{ fontSize:10, color:T.text1, marginTop:2 }}>Traité par : {req.traite_par}</div>
                  </div>
                </div>
                {req.motif_refus&&(
                  <div style={{ marginTop:10, padding:"8px 12px", background:`${T.red}10`, border:`1px solid ${T.red}20`, borderRadius:6 }}>
                    <div style={{ fontSize:9, color:T.red, fontWeight:700, textTransform:"uppercase", letterSpacing:"0.07em", marginBottom:3 }}>motif_refus</div>
                    <div style={{ fontSize:12, color:T.text1 }}>{req.motif_refus}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Panel>
      )}
      </React.Fragment>}
    </div>
  );
}

// FIX #4 : AuditPage lit auditLogData depuis le contexte
function AuditPage() {
  const { auditLogData, loading } = useData();
  return (
    <Panel>
      <STitle right={
        <div style={{ display:"flex", gap:8, alignItems:"center" }}>
          <span style={{ fontSize:10, color:T.text2 }}>historique_operations — colonne: timestamp</span>
          <button style={{ background:`${T.gold}15`, border:`1px solid ${T.gold}40`, color:T.gold, padding:"4px 12px", borderRadius:5, fontSize:10, fontWeight:700, cursor:"pointer" }}>Export CSV (UC-SA-05)</button>
        </div>
      }>Journal d'audit — {auditLogData.length} entrée(s)</STitle>
      {loading["audit"] ? <Loader label="Chargement du journal…"/> : auditLogData.length === 0 ? (
        <Empty label="Aucune opération enregistrée"/>
      ) : (<React.Fragment>
      <div style={{ display:"grid", gridTemplateColumns:"8px 120px 1fr 120px 80px 100px", gap:10, marginBottom:8, padding:"4px 10px" }}>
        {["","Opération","Acteur","Diplôme","Institution","Horodatage"].map((h,i)=>(
          <div key={i} style={{ fontSize:9, fontWeight:800, color:T.text2, textTransform:"uppercase", letterSpacing:"0.08em" }}>{h}</div>
        ))}
      </div>
      {auditLogData.map((e,i)=>(
        <div key={i}
          onMouseEnter={el=>el.currentTarget.style.background=`${T.bg3}60`}
          onMouseLeave={el=>el.currentTarget.style.background=""}
          style={{ display:"grid", gridTemplateColumns:"8px 120px 1fr 120px 80px 100px", alignItems:"center", gap:10, padding:"10px 10px", borderBottom:`1px solid ${T.border}20`, transition:"background .1s" }}
        >
          <span style={{ width:6, height:6, borderRadius:"50%", background:e.color, boxShadow:`0 0 7px ${e.color}`, margin:"0 auto" }}/>
          <span style={{ fontSize:10, fontWeight:800, color:e.color, background:`${e.color}15`, padding:"2px 7px", borderRadius:4, fontFamily:"monospace", whiteSpace:"nowrap" }}>{e.type_operation}</span>
          <span style={{ fontSize:11, color:T.text1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{e.acteur}</span>
          <span style={{ fontSize:11, color:T.gold, fontFamily:"monospace", fontWeight:700 }}>{e.diplome_id}</span>
          <span style={{ fontSize:10, color:T.text2 }}>{e.inst}</span>
          <span style={{ fontSize:10, color:T.text2, textAlign:"right" }}>{e.timestamp}</span>
        </div>
      ))}
      </React.Fragment>)}
    </Panel>
  );
}

// ── App Shell ─────────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(() => {
    try { return localStorage.getItem("diplochain_token") || ""; } catch { return ""; }
  });

  // FIX #5 : tous les useState AVANT les useEffect (ordre des hooks stable)
  const [metricsToday,           setMetricsToday]           = useState(MOCK_METRICS_TODAY);
  const [metricsDaily,           setMetricsDaily]           = useState(MOCK_METRICS_DAILY);
  const [institutionsData,       setInstitutionsData]       = useState(MOCK_INSTITUTIONS);
  const [diplomesData,           setDiplomesData]           = useState(MOCK_DIPLOMES);
  const [studentsData,           setStudentsData]           = useState(MOCK_STUDENTS);
  const [retryAlertsData,        setRetryAlertsData]        = useState(MOCK_RETRY_ALERTS);
  const [pendingData,            setPendingData]            = useState(MOCK_PENDING_ALL);
  const [auditLogData,           setAuditLogData]           = useState(MOCK_AUDIT_LOG);
  const [validationRequestsData, setValidationRequestsData] = useState(MOCK_VALIDATION_REQUESTS);
  const [entreprisesData,        setEntreprisesData]        = useState(MOCK_ENTREPRISES);
  const [authSessionsData,       setAuthSessionsData]       = useState(MOCK_AUTH_SESSIONS);
  // loading[page] = true pendant le fetch, false après
  const [loading,                setLoading]                = useState({});
  const [page,                   setPage]                   = useState("overview");
  const [time,                   setTime]                   = useState(new Date());
  const [lastRefresh,            setLastRefresh]            = useState(new Date());
  const [nextRefresh,            setNextRefresh]            = useState(300);

  const setLoad = (key, val) => setLoading(l => ({ ...l, [key]: val }));

  const authHeaders = token ? { Authorization:`Bearer ${token}` } : {};

  const apiGet = useCallback(async path => {
    try {
      const resp = await fetch(path, { headers: authHeaders });
      if (resp.status === 401) { setToken(""); try { localStorage.removeItem("diplochain_token"); } catch {} return null; }
      if (!resp.ok) throw new Error(`GET ${path} → ${resp.status}`);
      return await resp.json();
    } catch (err) { console.warn(err); return null; }
  }, [token]);

  // Clock + auto-refresh
  useEffect(() => {
    const t = setInterval(() => {
      setTime(new Date());
      setNextRefresh(n => { if (n<=1) { setLastRefresh(new Date()); return 300; } return n-1; });
    }, 1000);
    return () => clearInterval(t);
  }, []);

  // Chargement métriques overview (au login + à chaque refresh)
  useEffect(() => {
    if (!token) return;
    setLoad("overview", true);
    Promise.all([
      apiGet("/admin/metrics").then(data => {
        if (data) setMetricsToday(Array.isArray(data) ? data[0] : data);
      }),
      apiGet("/admin/metrics/daily").then(data => {
        if (data) setMetricsDaily(data);
      }),
      apiGet("/admin/alerts/retry-worker").then(data => {
        if (data) setRetryAlertsData(applyNorm(data, normalizeRetryAlert, MOCK_RETRY_ALERTS));
      }),
      apiGet("/admin/audit").then(data => {
        if (data) setAuditLogData(applyNorm(data, normalizeAuditEntry, MOCK_AUDIT_LOG));
      }),
    ]).finally(() => setLoad("overview", false));
  }, [token, lastRefresh]);

  // Chargement données par page
  useEffect(() => {
    if (!token) return;
    setLoad(page, true);
    const done = () => setLoad(page, false);
    switch (page) {
      case "diplomes":
        apiGet("/diplomes/").then(d => {
          if (d) setDiplomesData(applyNorm(d, normalizeDiplome, MOCK_DIPLOMES));
        }).finally(done);
        break;
      case "etudiants":
        apiGet("/admin/students").then(d => {
          if (d) setStudentsData(applyNorm(d, x => x, MOCK_STUDENTS));
        }).finally(done);
        break;
      case "institutions":
        apiGet("/institutions/").then(d => {
          if (d) setInstitutionsData(applyNorm(d, x => x, MOCK_INSTITUTIONS));
        }).finally(done);
        break;
      case "blockchain":
        Promise.all([
          apiGet("/admin/alerts/retry-worker").then(d => {
            if (d) setRetryAlertsData(applyNorm(d, normalizeRetryAlert, MOCK_RETRY_ALERTS));
          }),
          apiGet("/admin/alerts/pending").then(d => {
            if (d) setPendingData(applyNorm(d, normalizeRetryAlert, MOCK_PENDING_ALL));
          }),
        ]).finally(done);
        break;
      case "entreprises":
        Promise.all([
          apiGet("/admin/entreprises/requests").then(d => {
            if (d) setValidationRequestsData(applyNorm(d, normalizeValidationRequest, MOCK_VALIDATION_REQUESTS));
          }),
          apiGet("/admin/entreprises").then(d => {
            if (d) setEntreprisesData(applyNorm(d, normalizeEntreprise, MOCK_ENTREPRISES));
          }),
          apiGet("/admin/entreprises/sessions").then(d => {
            if (d) setAuthSessionsData(applyNorm(d, normalizeAuthSession, MOCK_AUTH_SESSIONS));
          }),
        ]).finally(done);
        break;
      case "audit":
        apiGet("/admin/audit").then(d => {
          if (d) setAuditLogData(applyNorm(d, normalizeAuditEntry, MOCK_AUDIT_LOG));
        }).finally(done);
        break;
      default:
        setLoad(page, false);
        break;
    }
  }, [page, lastRefresh, token]);

  const mins = Math.floor(nextRefresh/60);
  const secs = nextRefresh%60;

  // FIX #2 : NAV calculé à partir du state (pas une constante module-level)
  const nav = buildNav(retryAlertsData.length, validationRequestsData.filter(r=>r.status==="EN_ATTENTE").length);

  const dataValues = {
    metricsToday, metricsDaily, institutionsData, diplomesData, studentsData,
    retryAlertsData, pendingData, auditLogData,
    validationRequestsData, entreprisesData, authSessionsData,
    loading,
  };

  const pagesMap = {
    overview:     <Overview setPage={setPage}/>,
    diplomes:     <DiplomesPage/>,
    etudiants:    <EtudiantsPage/>,
    institutions: <InstitutionsPage/>,
    entreprises:  <EntreprisesPage/>,
    blockchain:   <BlockchainPage/>,
    audit:        <AuditPage/>,
  };
  const pageTitles = {
    overview:"Vue d'ensemble", diplomes:"Diplômes",
    etudiants:"Étudiants — UC-SA-03", institutions:"Institutions — UC-SA-04/07",
    entreprises:"Entreprises & Accès Azure AD", blockchain:"Blockchain & Retry Worker — UC-SA-02",
    audit:"Journal d'audit",
  };

  if (!token) {
    return <Login onSuccess={t=>{ setToken(t); try { localStorage.setItem("diplochain_token",t); } catch {} }}/>;
  }

  return (
    <DataContext.Provider value={dataValues}>
      <div style={{ display:"flex", minHeight:"100vh", background:T.bg0, color:T.text0, fontFamily:"'DM Sans','Segoe UI',sans-serif", fontSize:14 }}>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=DM+Mono:wght@400;500&display=swap');
          *{box-sizing:border-box;margin:0;padding:0;}
          ::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:${T.border};border-radius:2px;}
          input::placeholder{color:${T.text2};}
        `}</style>

        {/* Sidebar */}
        <aside style={{ width:224, background:T.bg1, borderRight:`1px solid ${T.border}`, display:"flex", flexDirection:"column", flexShrink:0, position:"sticky", top:0, height:"100vh" }}>
          <div style={{ padding:"22px 18px 18px", borderBottom:`1px solid ${T.border}`, marginBottom:6 }}>
            <div style={{ display:"flex", alignItems:"center", gap:10 }}>
              <div style={{ width:34, height:34, borderRadius:9, background:`linear-gradient(135deg,${T.gold},${T.goldDim})`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:16, fontWeight:900, color:T.bg0 }}>◈</div>
              <div>
                <div style={{ fontSize:15, fontWeight:900, color:T.text0, letterSpacing:"-0.02em" }}>DiploChain</div>
                <div style={{ fontSize:9, color:T.goldDim, letterSpacing:"0.1em", textTransform:"uppercase" }}>Super Admin · v6</div>
              </div>
            </div>
          </div>
          <nav style={{ flex:1, padding:"6px 10px" }}>
            {nav.map(item=>{
              const active=page===item.id;
              return (
                <button key={item.id} onClick={()=>setPage(item.id)} style={{
                  width:"100%", display:"flex", alignItems:"center", gap:10,
                  padding:"9px 12px", borderRadius:8, marginBottom:2,
                  background:active?`${T.gold}18`:"transparent",
                  border:`1px solid ${active?T.gold+"40":"transparent"}`,
                  color:active?T.gold:T.text1,
                  cursor:"pointer", transition:"all .15s", textAlign:"left", fontSize:13, fontWeight:active?800:500,
                }}
                onMouseEnter={e=>{ if(!active){e.currentTarget.style.background=T.bg3;e.currentTarget.style.color=T.text0;}}}
                onMouseLeave={e=>{ if(!active){e.currentTarget.style.background="transparent";e.currentTarget.style.color=T.text1;}}}
                >
                  <span style={{ fontSize:15, width:18, textAlign:"center" }}>{item.icon}</span>
                  <span style={{ flex:1 }}>{item.label}</span>
                  {item.badge>0&&<span style={{ background:T.red, color:T.bg0, borderRadius:10, padding:"1px 6px", fontSize:9, fontWeight:900 }}>{item.badge}</span>}
                </button>
              );
            })}
          </nav>
          <div style={{ margin:"0 10px 8px", background:T.bg3, border:`1px solid ${T.border}`, borderRadius:8, padding:"8px 12px" }}>
            <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:4 }}>
              <span style={{ width:6, height:6, borderRadius:"50%", background:T.green, boxShadow:`0 0 6px ${T.green}` }}/>
              <span style={{ fontSize:9, color:T.text2, textTransform:"uppercase", letterSpacing:"0.08em", fontWeight:700 }}>Auto-refresh (5 min)</span>
            </div>
            <div style={{ height:2, background:T.bg0, borderRadius:1, overflow:"hidden" }}>
              <div style={{ height:"100%", width:`${((300-nextRefresh)/300)*100}%`, background:T.gold, borderRadius:1, transition:"width 1s linear" }}/>
            </div>
            <div style={{ fontSize:9, color:T.text2, marginTop:4, textAlign:"right" }}>Prochain refresh : {mins}:{String(secs).padStart(2,"0")}</div>
          </div>
          <div style={{ padding:"12px 18px", borderTop:`1px solid ${T.border}` }}>
            <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8 }}>
              <div style={{ width:28, height:28, borderRadius:"50%", background:`linear-gradient(135deg,${T.blue},${T.cyan})`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:10, fontWeight:900, color:T.bg0 }}>SA</div>
              <div style={{ flex:1, overflow:"hidden" }}>
                <div style={{ fontSize:11, fontWeight:800, color:T.text0, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>Super Admin</div>
                <div style={{ fontSize:9, color:T.text2 }}>RBAC: SUPER_ADMIN · JWT</div>
              </div>
            </div>
            <button onClick={()=>{ setToken(""); try{localStorage.removeItem("diplochain_token");}catch{} }} style={{ width:"100%", padding:6, fontSize:10, borderRadius:6, background:`${T.red}20`, color:T.red, border:`1px solid ${T.red}50`, cursor:"pointer" }}>
              Se déconnecter
            </button>
          </div>
        </aside>

        {/* Main */}
        <main style={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden" }}>
          <header style={{ height:54, background:T.bg1, borderBottom:`1px solid ${T.border}`, display:"flex", alignItems:"center", padding:"0 22px", gap:14, flexShrink:0, position:"sticky", top:0, zIndex:10 }}>
            <h1 style={{ fontSize:15, fontWeight:800, color:T.text0, flex:1 }}>{pageTitles[page]}</h1>
            <div style={{ display:"flex", alignItems:"center", gap:12 }}>
              {["Fabric","IPFS","PDF Microservice"].map(s=>(
                <div key={s} style={{ display:"flex", alignItems:"center", gap:5, fontSize:10, color:T.text1 }}>
                  <span style={{ width:5, height:5, borderRadius:"50%", background:T.green, boxShadow:`0 0 5px ${T.green}` }}/>
                  {s}
                </div>
              ))}
              <div style={{ width:1, height:14, background:T.border }}/>
              <div style={{ fontSize:10, color:T.text2, fontFamily:"DM Mono, monospace" }}>{time.toLocaleTimeString("fr-FR")}</div>
            </div>
          </header>
          <div style={{ flex:1, padding:20, overflowY:"auto" }}>
            {pagesMap[page]}
          </div>
        </main>
      </div>
    </DataContext.Provider>
    
  );
}