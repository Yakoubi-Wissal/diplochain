// generic API service layer - base URL and helpers
const BASE = "/api";

async function get(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

export function fetchDiplomas() {
  return get("/diplomas");
}

export function fetchEnterprises() {
  return get("/enterprises");
}

export function fetchBlockchainStatus() {
  return get("/blockchain/status");
}

export function fetchBlockchainTxs() {
  return get("/blockchain/transactions");
}

export function fetchRetryStatus() {
  return get("/retry/status");
}

export function fetchAuditLogs(params = "") {
  return get(`/audit/logs${params}`);
}

export function fetchSystemHealth() {
  return get("/system/health");
}

// public verification endpoint (by ID or QR token)
export function fetchVerification(identifier) {
  return get(`/verify/${identifier}`);
}
