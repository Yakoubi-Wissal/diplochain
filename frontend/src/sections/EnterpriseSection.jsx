import React from "react";
import { useRealtimeData } from "../hooks/useRealtimeData";
import { fetchEnterprises } from "../api/apiService";
import { SimpleLine } from "../components/Charts";
import PaginatedTable from "../components/PaginatedTable";

export default function EnterpriseSection() {
  const { data, loading } = useRealtimeData(fetchEnterprises);
  if (loading) return <div>Loading enterprises…</div>;
  if (!data) return <div>No data</div>;

  // prepare status counts for chart
  const byStatus = {};
  data.forEach(e => {
    const s = e.status || 'unknown';
    byStatus[s] = (byStatus[s] || 0) + 1;
  });
  const chartData = Object.entries(byStatus).map(([status, count])=>({ status, count }));

  const columns = [
    { header:'Name', render: e=>e.name },
    { header:'Azure tenant', render: e=>e.tenant },
    { header:'Status', render: e=>e.status },
    { header:'Permissions', render: e=>e.permissions },
  ];

  return (
    <div>
      <h2>Enterprise Access</h2>
      <div style={{ marginBottom:20 }}>
        <SimpleLine data={chartData} xKey="status" dataKey="count" stroke="#82ca9d" />
      </div>
      <PaginatedTable columns={columns} data={data} pageSize={20} exportFilename="enterprises.csv" />
    </div>
  );
}
