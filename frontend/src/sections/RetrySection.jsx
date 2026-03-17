import React from "react";
import { useRealtimeData } from "../hooks/useRealtimeData";
import { fetchRetryStatus } from "../api/apiService";
import { SimpleLine } from "../components/Charts";

export default function RetrySection() {
  const { data, loading } = useRealtimeData(fetchRetryStatus);
  if (loading) return <div>Loading retry status…</div>;
  if (!data) return <div>No data</div>;

  const chartData = [
    { label: 'queue', count: data.queue_size || 0 }
  ];

  return (
    <div>
      <h2>Retry Worker Monitoring</h2>
      <div style={{ display:'flex', gap:12, flexWrap:'wrap', marginBottom:12 }}>
        <div>Worker running: {data.running ? 'yes' : 'no'}</div>
        <div>Queue size: {data.queue_size}</div>
        <div>Last execution: {data.last_execution}</div>
        <div>Failures: {data.failed_retries}</div>
      </div>
      <div style={{ marginBottom:20 }}>
        <h4>Queue size snapshot</h4>
        <SimpleLine data={chartData} xKey="label" dataKey="count" />
      </div>
    </div>
  );
}
