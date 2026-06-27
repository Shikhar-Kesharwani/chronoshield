/* hooks/useMetricStream.js — SSE hook for live data */
import { useState, useEffect, useRef, useCallback } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const MAX_POINTS = 300;

export function useMetricStream(targetMetric = "cpu") {
  const [points,    setPoints]    = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [connected, setConnected] = useState(false);
  const [error,     setError]     = useState(null);
  const [stats,     setStats]     = useState(null);
  const esRef = useRef(null);

  const fetchStats = useCallback(async () => {
    try {
      const r = await fetch(`${API_BASE}/api/stats?metric=${targetMetric}`);
      const d = await r.json();
      setStats(d.stats);
    } catch (_) {}
  }, [targetMetric]);

  useEffect(() => {
    // Reset state on metric change
    setPoints([]);
    setAnomalies([]);
    setStats(null);
    
    // Poll stats every 10 s
    fetchStats();
    const statsInterval = setInterval(fetchStats, 10_000);

    // Connect SSE
    const es = new EventSource(`${API_BASE}/api/stream`);
    esRef.current = es;

    es.onopen = () => { setConnected(true); setError(null); };

    es.onmessage = (evt) => {
      try {
        const point = JSON.parse(evt.data);
        if (point.metric !== targetMetric) return; // Strict metric filtering
        
        setPoints(prev => {
          const next = [...prev, point];
          return next.length > MAX_POINTS ? next.slice(next.length - MAX_POINTS) : next;
        });
        if (point.z_anomaly || point.if_anomaly) {
          setAnomalies(prev => [point, ...prev].slice(0, 50));
        }
      } catch (_) {}
    };

    es.onerror = () => {
      setConnected(false);
      setError('Stream disconnected. Retrying…');
    };

    return () => {
      es.close();
      clearInterval(statsInterval);
    };
  }, [fetchStats, targetMetric]);

  const injectAnomaly = useCallback(async () => {
    try {
      await fetch(`${API_BASE}/api/inject`, { method: 'POST' });
    } catch (e) {
      console.error('Inject failed:', e);
    }
  }, []);

  return { points, anomalies, connected, error, stats, injectAnomaly };
}
