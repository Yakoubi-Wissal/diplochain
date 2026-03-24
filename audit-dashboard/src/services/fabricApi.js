/**
 * fabricApi.js — Client REST vers fabric-api-server (port 4001)
 * ─────────────────────────────────────────────────────────────────────
 * Remplace l'URL de base par celle de ton orchestrateur :
 *   REACT_APP_FABRIC_API=http://localhost:4001
 */

const BASE_URL = "http://localhost:4001";

// ─── Timeout helper ───────────────────────────────────────────────────
const fetchWithTimeout = async (url, options = {}, timeout = 10000) => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(id);
    if (!res.ok) {
      const error = await res.text();
      throw new Error(error || `HTTP ${res.status}`);
    }
    return res.json();
  } catch (err) {
    clearTimeout(id);
    if (err.name === "AbortError") throw new Error("Timeout — fabric-api-server injoignable");
    throw err;
  }
};

const getHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("diplochain_token") || ""}`,
});

// ─── Données simulées (désactiver quand le backend est prêt) ──────────
const MOCK = false;

const MOCK_DATA = {
  network: {
    orderer: { name: "orderer.diplochain.local", port: 7050, status: "running", blockHeight: 142, uptime: "3d 14h" },
    peer:    { name: "peer0.diplochain.local",   port: 7051, status: "running", endorsements: 89, uptime: "3d 14h" },
    couchdb: { name: "couchdb0.diplochain.local", port: 5984, status: "running", docs: 237 },
    ca:      { name: "fabric-ca.diplochain.local", port: 7054, status: "running" },
  },
  channels: [
    { id: "channel-1", institution: "Université de Tunis", institutionId: 1, height: 87, txCount: 54, chaincode: "diplochain v1.0", status: "active", created: "2026-03-18" },
    { id: "channel-2", institution: "ESPRIT",              institutionId: 2, height: 34, txCount: 21, chaincode: "diplochain v1.0", status: "active", created: "2026-03-18" },
    { id: "channel-42", institution: "INSAT",              institutionId: 42, height: 21, txCount: 14, chaincode: "diplochain v1.0", status: "active", created: "2026-03-19" },
  ],
  transactions: [
    { txId: "bff1a1b7acae9cfa7a6a5b0a81d711f074a3ff41", type: "RegisterDiploma", channel: "channel-1", institution: "Univ. Tunis", student: "Ahmed Ben Ali",    status: "VALID",   timestamp: "2026-03-18 12:00:16", block: 87 },
    { txId: "dd8eb373a67d3ce09f5db4e0101b30c7ef067d77", type: "RegisterDiploma", channel: "channel-2", institution: "ESPRIT",      student: "Sarra Trabelsi",  status: "VALID",   timestamp: "2026-03-18 11:45:02", block: 34 },
    { txId: "a91c3d2e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b",  type: "VerifyDiploma",   channel: "channel-1", institution: "Univ. Tunis", student: "Mohamed Khelifi", status: "VALID",   timestamp: "2026-03-18 11:30:44", block: 86 },
    { txId: "f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4",  type: "RevokeDiploma",   channel: "channel-42", institution: "INSAT",      student: "Leila Mansour",   status: "VALID",   timestamp: "2026-03-18 10:15:33", block: 21 },
    { txId: "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a",  type: "RegisterDiploma", channel: "channel-1", institution: "Univ. Tunis", student: "Ines Chaouachi",  status: "VALID",   timestamp: "2026-03-18 09:58:11", block: 85 },
    { txId: "9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e",  type: "RegisterDiploma", channel: "channel-42", institution: "INSAT",     student: "Rania Hamdi",     status: "PENDING", timestamp: "2026-03-18 08:44:22", block: null },
  ],
  logs: [
    { t: new Date(Date.now() - 2000).toISOString(),  level: "INFO",  src: "orderer",        msg: "Raft leader 1 elected at term 6 channel=channel-1" },
    { t: new Date(Date.now() - 6000).toISOString(),  level: "INFO",  src: "peer0",          msg: "Successfully committed chaincode diplochain on channel-1" },
    { t: new Date(Date.now() - 14000).toISOString(), level: "INFO",  src: "blockchain-svc", msg: "RegisterDiploma TX committed: bff1a1b7..." },
    { t: new Date(Date.now() - 25000).toISOString(), level: "WARN",  src: "retry-worker",   msg: "Diploma 9e0f1a2b PENDING — retry attempt 1/5" },
    { t: new Date(Date.now() - 40000).toISOString(), level: "ERROR", src: "fabric-ca",      msg: "Certificate renewal needed in 14 days" },
  ],
};

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

// ─── API publique ─────────────────────────────────────────────────────

/** État des nœuds Fabric */
export const getNetworkStatus = async () => {
  if (MOCK) { await delay(400); return MOCK_DATA.network; }
  return fetchWithTimeout(`${BASE_URL}/api/fabric/network/status`, { headers: getHeaders() });
};

/** Liste des canaux */
export const getChannels = async () => {
  if (MOCK) { await delay(300); return MOCK_DATA.channels; }
  return fetchWithTimeout(`${BASE_URL}/api/fabric/channels`, { headers: getHeaders() });
};

/** Historique des transactions */
export const getTransactions = async (params = {}) => {
  if (MOCK) { await delay(350); return MOCK_DATA.transactions; }
  const qs = new URLSearchParams(params).toString();
  return fetchWithTimeout(`${BASE_URL}/api/fabric/transactions${qs ? `?${qs}` : ""}`, { headers: getHeaders() });
};

/** Logs réseau */
export const getLogs = async (limit = 50) => {
  if (MOCK) { await delay(200); return MOCK_DATA.logs; }
  return fetchWithTimeout(`${BASE_URL}/api/fabric/logs?limit=${limit}`, { headers: getHeaders() });
};

/**
 * Créer un nouveau canal institution
 * Exécute create-channel.sh <institutionId> via l'orchestrateur
 */
export const createChannel = async (institutionId) => {
  if (MOCK) {
    await delay(2200);
    return { success: true, channelId: `channel-${institutionId}`, msg: "Canal créé et chaincode déployé" };
  }
  return fetchWithTimeout(`${BASE_URL}/api/fabric/channel/create`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ institutionId: parseInt(institutionId, 10) }),
  });
};

/**
 * Invoquer le chaincode (RegisterDiploma, RevokeDiploma, etc.)
 * @param {object} payload - { fn, channel, diplomeId, hash, ipfsCid, institutionId, etudiantId, date }
 * @returns {{ txId, block, status }}
 */
export const invokeChaincode = async (payload) => {
  if (MOCK) {
    await delay(1800);
    const txId = Array.from({ length: 40 }, () => Math.floor(Math.random() * 16).toString(16)).join("") + "...";
    return { txId, block: 143, status: "VALID" };
  }
  return fetchWithTimeout(`${BASE_URL}/api/fabric/chaincode/invoke`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
};

/**
 * Générer un rapport
 * @param {string} type - "activity" | "diplomes" | "institutions" | "security"
 * @param {string} format - "json" | "pdf"
 */
export const generateReport = async (type, format = "json") => {
  if (MOCK) {
    await delay(1500);
    return {
      report: `DiploChain ${type}`,
      generated: new Date().toISOString(),
      format,
      summary: { transactions: 142, diplomes: 89, channels: 3 },
      data: MOCK_DATA.transactions.slice(0, 5),
    };
  }
  if (format === "pdf") {
    // Téléchargement direct du PDF
    const res = await fetch(`${BASE_URL}/api/fabric/reports/${type}?format=pdf`, { headers: getHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = `diplochain_${type}.pdf`; a.click();
    URL.revokeObjectURL(url);
    return { success: true };
  }
  return fetchWithTimeout(`${BASE_URL}/api/fabric/reports/${type}?format=json`, { headers: getHeaders() });
};


export const createStudent = async (data) => {
  return fetchWithTimeout(`${BASE_URL}/api/students/`, {
    method: "POST", headers: getHeaders(), body: JSON.stringify(data),
  });
};

export const createInstitution = async (data) => {
  return fetchWithTimeout(`${BASE_URL}/api/institutions/`, {
    method: "POST", headers: getHeaders(), body: JSON.stringify(data),
  });
};

export const loginAdmin = async () => {
  return fetchWithTimeout(`${BASE_URL}/api/users/auth/login`, {
    method: "POST", headers: getHeaders(),
  });
};

/** Récupérer les statistiques globales */
export const getStats = async () => {
  if (MOCK) { await delay(200); return { total_tx: 142, diplomas: 89, verifications: 45, revocations: 8 }; }
  return fetchWithTimeout(`${BASE_URL}/api/fabric/stats`, { headers: getHeaders() });
};

/** Rapport complet du projet */
export const getFullProjectReport = async () => {
  return fetchWithTimeout(`${BASE_URL}/api/fabric/report-full-project`, { headers: getHeaders() });
};

// Objet nommé pour import groupé
export const fabricApi = { 
  getNetworkStatus, 
  getChannels, 
  getTransactions, 
  getLogs, 
  getStats,
  getFullProjectReport,
  createChannel, 
  invokeChaincode, 
  generateReport, 
  createStudent, 
  createInstitution, 
  loginAdmin 
};
