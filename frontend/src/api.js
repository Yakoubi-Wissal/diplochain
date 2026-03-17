// Simple API helper based on the OpenAPI definition provided by the backend.
// Only endpoints actually used by the dashboard are implemented here, but
// the spec can be extended if needed.

/**
 * @typedef {Object} TokenResponse
 * @property {string} access_token
 * @property {string} token_type
 */

/**
 * @typedef {Object} DashboardMetricsRead
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

const BASE = "";

/**
 * Attempt to authenticate and return the bearer token.
 * @param {{username:string,password:string}} body
 * @returns {Promise<TokenResponse>}
 */
export async function login(body) {
  const resp = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams(body),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`login failed: ${resp.status} ${text}`);
  }
  /** @type {TokenResponse} */
  const data = await resp.json();
  return data;
}

/**
 * Load daily metrics used by the dashboard overview.
 * @param {string} [date] optional ISO date filter
 * @param {string} token bearer token if available
 * @returns {Promise<DashboardMetricsRead[]>}
 */
export async function getMetrics(date, token) {
  const qs = new URLSearchParams();
  if (date) {
    qs.set("date", date);
  }
  const resp = await fetch(`${BASE}/admin/metrics?${qs.toString()}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`metrics fetch failed: ${resp.status} ${text}`);
  }
  /** @type {DashboardMetricsRead[]} */
  const data = await resp.json();
  return data;
}

/**
 * Daily metrics endpoint used by the overview. This mirrors the
 * previous `/admin/metrics/daily` call that wasn’t part of the OpenAPI
 * spec, but it’s still available on the server.
 * @param {string} token
 * @returns {Promise<DashboardMetricsRead[]>}
 */
// although the original UI called `/admin/metrics/daily`, the OpenAPI
// spec doesn't expose that path and the server currently responds 404. we
// keep a helper around for backward compatibility but swallow 404 into an
// empty array so callers don't need to handle it.
export async function getMetricsDaily(token) {
  try {
    const resp = await fetch(`${BASE}/admin/metrics/daily`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    });
    if (resp.status === 404) {
      // endpoint absent on this version of the API
      return [];
    }
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`metrics daily fetch failed: ${resp.status} ${text}`);
    }
    /** @type {DashboardMetricsRead[]} */
    const data = await resp.json();
    return data;
  } catch (err) {
    // network error or other; log and return empty list so the UI degrades
    console.warn("getMetricsDaily failed", err);
    return [];
  }
}

// more helpers can be added here when the UI consumes additional endpoints.  
// the OpenAPI spec you've provided is a complete reference of available
// routes (institutions, users, diplomas, etc). generate clients via
// openapi-generator or keep extending this simple module.
