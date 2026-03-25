/**
 * useFabric.js — Hooks React pour les données Fabric
 * ─────────────────────────────────────────────────────
 * Gère : loading, error, refresh, polling automatique
 */

import { useState, useEffect, useCallback, useRef } from "react";
import {
  getNetworkStatus,
  getChannels,
  getTransactions,
  getLogs,
  getStats,
  getStabilityMetrics,
  getStabilityHistory
} from "../services/fabricApi";

// ─── Hook générique avec polling ──────────────────────────────────────
function useFabricData(fetcher, pollInterval = null) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const mounted = useRef(true);

  const fetch = useCallback(async () => {
    try {
      const result = await fetcher();
      if (mounted.current) { setData(result); setError(null); }
    } catch (err) {
      if (mounted.current) setError(err.message);
    } finally {
      if (mounted.current) setLoading(false);
    }
  }, [fetcher]);

  useEffect(() => {
    mounted.current = true;
    fetch();
    if (pollInterval) {
      const id = setInterval(fetch, pollInterval);
      return () => { clearInterval(id); mounted.current = false; };
    }
    return () => { mounted.current = false; };
  }, [fetch, pollInterval]);

  return { data, loading, error, refresh: fetch };
}

/** État des nœuds Fabric — polling toutes les 15s */
export const useFabricNetwork = () =>
  useFabricData(useCallback(() => getNetworkStatus(), []), 15000);

/** Liste des canaux — polling toutes les 30s */
export const useFabricChannels = () =>
  useFabricData(useCallback(() => getChannels(), []), 30000);

/** Transactions — polling toutes les 10s */
export const useFabricTransactions = (params = {}) =>
  useFabricData(useCallback(() => getTransactions(params), []), 10000);

/** Logs — accumulés côté client, pas de polling (géré dans LogsTab) */
export const useFabricLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLogs(30)
      .then(setLogs)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return { logs, loading };
};

/** Statistiques globales — polling toutes les 5s */
export const useFabricStats = () =>
  useFabricData(useCallback(() => getStats(), []), 5000);

/** Métriques de stabilité — polling toutes les 30s */
export const useStabilityStats = () =>
  useFabricData(useCallback(() => getStabilityMetrics(), []), 30000);

/** Historique de stabilité */
export const useStabilityHistory = () =>
  useFabricData(useCallback(() => getStabilityHistory(), []), 60000);
