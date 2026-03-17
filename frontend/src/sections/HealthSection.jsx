import React from "react";
import { useRealtimeData } from "../hooks/useRealtimeData";
import { fetchSystemHealth } from "../api/apiService";
import { SimpleLine } from "../components/Charts";

export default function HealthSection() {
  const { data, loading } = useRealtimeData(fetchSystemHealth);
  if (loading) return <div>Loading system health…</div>;
  if (!data) return <div>No health data</div>;

  // expected schema example:
  // {
  //   uptime: "12h",
  //   cpu_load: 0.3,
  //   memory_usage: 0.6,
  //   disk_free: 102400000,
  //   services: {db:'ok',cache:'warn',api:'ok'}
  // }

  const renderStatus = (val) => {
    if (val === true || String(val).toLowerCase() === 'ok') return 'lightgreen';
    if (String(val).toLowerCase().includes('warn')) return 'yellow';
    if (val === false || String(val).toLowerCase().includes('fail')) return '#f99';
    return '#eee';
  };

  // numeric values chart
  const numeric = Object.entries(data).filter(([k,v])=> typeof v === 'number');
  const chartData = numeric.map(([k,v])=>({ label:k, value:v }));

  return (
    <div>
      <h2>System Health</h2>
      <div style={{ display:'flex', gap:12, flexWrap:'wrap', marginBottom:20 }}>
        {Object.entries(data).map(([k, v]) => (
          <div
            key={k}
            style={{
              padding:6,
              borderRadius:4,
              background: renderStatus(v),
              minWidth:120,
            }}
          >
            <strong>{k}</strong>: {String(v)}
          </div>
        ))}
      </div>
      {chartData.length > 0 && (
        <div>
          <h4>Numeric metrics</h4>
          <SimpleLine data={chartData} xKey="label" dataKey="value" />
        </div>
      )}
    </div>
  );
}
