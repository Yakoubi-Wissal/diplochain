import React from "react";
import { useRealtimeData } from "../hooks/useRealtimeData";
import { fetchDiplomas } from "../api/apiService";
import { SimpleLine } from "../components/Charts";
import PaginatedTable from "../components/PaginatedTable";

export default function DiplomasSection() {
  const { data, loading } = useRealtimeData(fetchDiplomas);

  if (loading) return <div>Loading diplomas…</div>;
  if (!data) return <div>No data</div>;

  // compute aggregates
  const total = data.length;
  const verified = data.filter(d=>d.status === "ORIGINAL" || d.status === "MICROSERVICE").length;
  const pending = data.filter(d=>d.status === "PENDING_BLOCKCHAIN").length;
  const rejected = data.filter(d=>d.status === "REVOQUE").length;

  // prepare chart data: diplomas created per day (assuming created_at field)
  const byDay = {};
  data.forEach(d=>{
    const day = d.created_at ? d.created_at.split('T')[0] : 'unknown';
    byDay[day] = (byDay[day]||0)+1;
  });
  const chartData = Object.entries(byDay).map(([date,count])=>({ date, count }));

  // simple filter state
  const [filter, setFilter] = React.useState("");
  const filtered = data.filter(d=>
    !filter ||
    String(d.id).includes(filter) ||
    d.student?.toLowerCase().includes(filter.toLowerCase()) ||
    d.university?.toLowerCase().includes(filter.toLowerCase())
  );

  // table columns definition
  const columns = [
    { header:'ID', render: d=>d.id },
    { header:'Student', render: d=>d.student },
    { header:'University', render: d=>d.university },
    { header:'Status', render: d=>d.status },
    { header:'Hash', render: d=>(
        <span style={{ fontFamily:'monospace', fontSize:10 }}>{d.blockchain_hash}</span>
      ) },
    { header:'Created At', render: d=>(<span style={{ fontSize:10 }}>{d.created_at}</span>) },
  ];

  return (
    <div>
      <h2>Diplomas Monitoring</h2>
      <div style={{ display:'flex', gap:12, flexWrap:'wrap', marginBottom:12 }}>
        <div>Total: {total}</div>
        <div>Verified: {verified}</div>
        <div>Pending: {pending}</div>
        <div>Rejected: {rejected}</div>
      </div>
      {/* chart */}
      <div style={{ marginBottom:20 }}>
        <h4>Created per day</h4>
        <SimpleLine data={chartData} dataKey="count" />
      </div>

      <div style={{ marginBottom:10 }}>
        <input
          placeholder="search id, student, university"
          value={filter}
          onChange={e=>setFilter(e.target.value)}
          style={{ padding:6, width:300, borderRadius:4, border:'1px solid #444' }}
        />
      </div>

      <PaginatedTable
        columns={columns}
        data={filtered}
        pageSize={25}
        exportFilename="diplomas.csv"
      />
    </div>
  );
}
