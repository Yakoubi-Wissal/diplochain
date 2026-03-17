import React from "react";
import { useRealtimeData } from "../hooks/useRealtimeData";
import { fetchAuditLogs } from "../api/apiService";
import { SimpleLine } from "../components/Charts";
import PaginatedTable from "../components/PaginatedTable";

export default function AuditSection() {
  const { data, loading } = useRealtimeData(() => fetchAuditLogs());
  if (loading) return <div>Loading audit log…</div>;
  if (!data) return <div>No data</div>;

  const [filter, setFilter] = React.useState("");
  const filtered = data.filter(e=>
    !filter ||
    e.user?.toLowerCase().includes(filter.toLowerCase()) ||
    e.action?.toLowerCase().includes(filter.toLowerCase())
  );

  // chart of events by day
  const byDay = {};
  data.forEach(e=>{
    const day = e.timestamp ? e.timestamp.split('T')[0] : 'unknown';
    byDay[day] = (byDay[day]||0)+1;
  });
  const chartData = Object.entries(byDay).map(([date,count])=>({ date,count }));

  const columns = [
    { header:'Timestamp', render: e=>(<span style={{fontSize:10}}>{e.timestamp}</span>) },
    { header:'User', render: e=>e.user },
    { header:'Action', render: e=>e.action },
    { header:'Resource', render: e=>e.resource },
    { header:'Result', render: e=>e.result },
    { header:'IP', render: e=>e.ip },
  ];

  return (
    <div>
      <h2>Audit Log</h2>
      <div style={{ marginBottom:10 }}>
        <input
          placeholder="filter by user/action"
          value={filter}
          onChange={e=>setFilter(e.target.value)}
          style={{ padding:6, width:300, borderRadius:4, border:'1px solid #444' }}
        />
      </div>
      <div style={{ marginBottom:20 }}>
        <h4>Events per day</h4>
        <SimpleLine data={chartData} dataKey="count" />
      </div>
      <PaginatedTable columns={columns} data={filtered} pageSize={30} exportFilename="audit.csv" />
    </div>
  );
}
