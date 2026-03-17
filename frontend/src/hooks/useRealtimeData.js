import { useEffect, useState, useCallback } from "react";

export function useRealtimeData(fetcher, interval = 5000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const d = await fetcher();
      setData(d);
    } catch (e) {
      console.warn(e);
    } finally {
      setLoading(false);
    }
  }, [fetcher]);

  useEffect(() => {
    load();
    const id = setInterval(load, interval);
    return () => clearInterval(id);
  }, [load, interval]);

  return { data, loading };
}