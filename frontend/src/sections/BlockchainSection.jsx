import React from "react";
import { useRealtimeData } from "../hooks/useRealtimeData";
import { fetchBlockchainStatus, fetchBlockchainTxs } from "../api/apiService";
import { SimpleLine } from "../components/Charts";
import PaginatedTable from "../components/PaginatedTable";

export default function BlockchainSection() {
  const { data: status, loading: l1 } = useRealtimeData(fetchBlockchainStatus);
  const { data: txs, loading: l2 } = useRealtimeData(fetchBlockchainTxs);
  const loading = l1 || l2;
  if (loading) return <div>Loading blockchain …</div>;
  if (!status) return <div>No status</div>;

  // transactions per day line data
  const txChart = {};
  if (txs) {
    txs.forEach(tx=>{
      const day = tx.timestamp ? tx.timestamp.split('T')[0] : 'unknown';
      txChart[day] = (txChart[day]||0)+1;
    });
  }
  const chartData = Object.entries(txChart).map(([date,count])=>({ date, count }));

  const columns = [
    { header:'Tx ID', render: t=>t.id },
    { header:'Status', render: t=>t.status },
    { header:'Timestamp', render: t=>t.timestamp },
  ];

  return (
    <div>
      <h2>Blockchain Monitoring</h2>
      <div style={{ display:'flex', gap:12, flexWrap:'wrap', marginBottom:12 }}>
        <div>Total txs: {status.total_transactions}</div>
        <div>Last block: {status.last_block_hash}</div>
        <div>Pending: {status.pending_transactions}</div>
        <div>Failed: {status.failed_transactions}</div>
        <div>Retry queue: {status.retry_queue_size}</div>
      </div>
      <div style={{ marginBottom:20 }}>
        <h4>Transactions per day</h4>
        <SimpleLine data={chartData} dataKey="count" />
      </div>
      <h3>Recent transactions</h3>
      <PaginatedTable columns={columns} data={txs || []} pageSize={20} exportFilename="txs.csv" />
    </div>
  );
}
