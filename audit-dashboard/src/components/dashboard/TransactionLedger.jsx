import React, { useState } from 'react';
import { C } from './DashboardTokens';
import { Card, Badge, Dot, DCButton, Spinner } from './UIPrimitives';
import { invokeChaincode, getTransactionHistory } from '../../services/fabricApi';

const TYPE_COLORS = { RegisterDiploma: C.blue, VerifyDiploma: C.teal, RevokeDiploma: C.red, QueryDiploma: C.violet };

export default function TransactionLedger({ transactions, loading, onToast }) {
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [historyModal, setHistoryModal] = useState(null); // { id: "", data: [] }
  const [form, setForm] = useState({ fn: "RegisterDiploma", channel: "channel-1", diplomeId: "", hash: "", ipfsCid: "", institutionId: "1", etudiantId: "", date: new Date().toISOString().slice(0, 10) });
  const [invoking, setInvoking] = useState(false);
  const [fetchingHistory, setFetchingHistory] = useState(false);
  const [result, setResult] = useState(null);

  const types = ["ALL", "RegisterDiploma", "VerifyDiploma", "RevokeDiploma", "QueryDiploma"];
  
  const handleTrace = async (id, channel) => {
    setFetchingHistory(id); // Set ID instead of just boolean
    try {
      const history = await getTransactionHistory(id, channel);
      setHistoryModal({ id, data: history });
    } catch (e) {
      onToast(`Trace error: ${e.message}`, "error");
    } finally {
      setFetchingHistory(false);
    }
  };
  const filtered = (transactions || []).filter((tx) =>
    (filter === "ALL" || tx.type === filter) &&
    (!search || tx.txId?.includes(search) || tx.student?.toLowerCase().includes(search.toLowerCase()) || tx.channel?.includes(search))
  );

  const handleInvoke = async () => {
    setInvoking(true);
    setResult(null);
    try {
      const res = await invokeChaincode({ ...form });
      setResult({ ok: true, txId: res.txId, block: res.block });
      onToast(`TX: ${form.fn} validated on-chain`, "success");
    } catch (e) {
      setResult({ ok: false, msg: e.message });
      onToast(`Chaincode Error: ${e.message}`, "error");
    } finally {
      setInvoking(false);
    }
  };

  return (
    <Card icon="⚡" title="Blockchain Ledger Explorer" action={
      <DCButton variant="teal" small onClick={() => setShowModal(true)} icon="⚡">Invoke Chaincode</DCButton>
    }>
      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
        {types.map((t) => (
          <button key={t} onClick={() => setFilter(t)} style={{
            padding: "6px 14px", borderRadius: 8, fontSize: 11, cursor: "pointer",
            background: filter === t ? `${TYPE_COLORS[t] || C.blue}20` : "transparent",
            color: filter === t ? (TYPE_COLORS[t] || C.blue) : C.textSec,
            border: `1px solid ${filter === t ? `${TYPE_COLORS[t] || C.blue}50` : C.border}`,
            fontFamily: C.sans, fontWeight: 600, transition: "all .2s",
          }}>{t}</button>
        ))}
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by TXID, student, or channel..."
          style={{ marginLeft: "auto", padding: "8px 16px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, color: C.text, fontSize: 12, outline: "none", width: 280 }}
        />
      </div>

      <div style={{ overflowX: "auto", borderRadius: 12, border: `1px solid ${C.border}` }}>
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 800 }}>
          <thead>
            <tr style={{ background: C.surfaceHi, borderBottom: `1px solid ${C.border}` }}>
              {["Operation", "Transaction ID", "Channel", "Student / Owner", "Status", "Block", "Timestamp"].map((h) => (
                <th key={h} style={{ padding: "14px 18px", textAlign: "left", fontSize: 10, fontWeight: 700, color: C.textSec, textTransform: "uppercase", letterSpacing: ".08em" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={7} style={{ textAlign: "center", padding: 40 }}><Spinner size={24} /></td></tr>
            )}
            {filtered.map((tx, i) => (
              <tr key={tx.txId || i} className="dc-row" style={{ borderBottom: `1px solid ${C.border}30`, transition: "all 0.2s" }}>
                <td style={{ padding: "14px 18px" }}><Badge text={tx.type} color={TYPE_COLORS[tx.type] || C.textSec} /></td>
                <td style={{ padding: "14px 18px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontFamily: C.mono, fontSize: 11, color: C.textSec }}>{(tx.txId || "").slice(0, 12)}...</span>
                    <DCButton variant="ghost" small onClick={() => handleTrace(tx.txId, tx.channel)} icon="🔍" loading={fetchingHistory === tx.txId} />
                  </div>
                </td>
                <td style={{ padding: "14px 18px" }}><Badge text={tx.channel} color={C.blue} outline /></td>
                <td style={{ padding: "14px 18px", fontSize: 13, fontWeight: 600, color: C.text }}>{tx.student}</td>
                <td style={{ padding: "14px 18px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Dot status={tx.status} pulse={tx.status === "PENDING"} />
                    <span style={{ fontSize: 12, fontWeight: 600, color: tx.status === "VALID" ? C.green : C.amber }}>{tx.status}</span>
                  </div>
                </td>
                <td style={{ padding: "14px 18px" }}><span style={{ fontFamily: C.mono, fontSize: 12, fontWeight: 700, color: tx.block ? C.teal : C.textMut }}>{tx.block ?? "-"}</span></td>
                <td style={{ padding: "14px 18px", fontSize: 11, color: C.textMut }}>{tx.timestamp}</td>
              </tr>
            ))}
            {!loading && filtered.length === 0 && (
              <tr><td colSpan={7} style={{ padding: "40px", textAlign: "center", color: C.textMut }}>No Ledger records found.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", backdropFilter: "blur(8px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div style={{ background: C.surface, border: `1px solid ${C.borderHi}`, borderRadius: 16, padding: 32, width: 520, maxHeight: "90vh", overflowY: "auto", boxShadow: C.shadow }}>
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8, color: C.text }}>Invoke Chaincode Engine</div>
            <div style={{ fontSize: 12, color: C.textMut, marginBottom: 24 }}>Bridge to <code style={{ color: C.blue }}>peer chaincode invoke</code></div>

            {[
              { label: "Contract Function", key: "fn", type: "select", opts: ["RegisterDiploma", "QueryDiploma", "VerifyDiploma", "RevokeDiploma", "QueryByInstitution"] },
              { label: "Target Channel", key: "channel", type: "select", opts: ["channel-1", "channel-2", "channel-42"] },
              { label: "Asset ID", key: "diplomeId", placeholder: "e.g. D-123" },
              { label: "Data Hash (SHA-256)", key: "hash", placeholder: "64-char hex string" },
              { label: "IPFS Reference (CID)", key: "ipfsCid", placeholder: "Qm..." },
            ].map((f) => (
              <div key={f.key} style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 11, color: C.textSec, display: "block", marginBottom: 6, textTransform: "uppercase", fontWeight: 700 }}>{f.label}</label>
                {f.type === "select" ? (
                  <select value={form[f.key]} onChange={(e) => setForm((p) => ({ ...p, [f.key]: e.target.value }))}
                    style={{ width: "100%", padding: "10px 14px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, color: C.text, fontSize: 13, fontFamily: C.mono, outline: "none" }}>
                    {f.opts.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : (
                  <input value={form[f.key]} onChange={(e) => setForm((p) => ({ ...p, [f.key]: e.target.value }))} placeholder={f.placeholder}
                    style={{ width: "100%", padding: "10px 14px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, color: C.text, fontSize: 13, fontFamily: C.mono, outline: "none" }} />
                )}
              </div>
            ))}

            {result && (
              <div style={{ padding: "14px", background: result.ok ? `${C.green}10` : `${C.red}10`, border: `1px solid ${result.ok ? C.green : C.red}40`, borderRadius: 10, marginBottom: 20 }}>
                {result.ok ? (
                  <>
                    <div style={{ fontSize: 13, color: C.green, fontWeight: 700 }}>✓ Ledger Commit Success</div>
                    <div style={{ fontSize: 10, fontFamily: C.mono, color: C.textSec, marginTop: 4 }}>TX: {result.txId}</div>
                    <div style={{ fontSize: 10, color: C.textSec }}>Block: {result.block}</div>
                  </>
                ) : (
                  <div style={{ fontSize: 13, color: C.red }}>✗ Chaincode Runtime Exception: {result.msg}</div>
                )}
              </div>
            )}

            <div style={{ display: "flex", gap: 12, justifyContent: "flex-end", marginTop: 12 }}>
              <DCButton variant="ghost" onClick={() => { setShowModal(false); setResult(null); }}>Discard</DCButton>
              <DCButton variant="teal" onClick={handleInvoke} loading={invoking} icon="⚡">Commit TX</DCButton>
            </div>
          </div>
        </div>
      )}

      {historyModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.85)", backdropFilter: "blur(10px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1100 }}>
          <div style={{ background: C.surface, border: `1px solid ${C.borderHi}`, borderRadius: 20, padding: 32, width: 650, maxHeight: "85vh", overflowY: "auto", boxShadow: C.shadow }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700, color: C.text }}>Blockchain Asset Lifecycle Trace</div>
                <div style={{ fontSize: 11, fontFamily: C.mono, color: C.blue, marginTop: 4 }}>ID: {historyModal.id}</div>
              </div>
              <DCButton variant="ghost" onClick={() => setHistoryModal(null)}>Close</DCButton>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 0, position: "relative", paddingLeft: 24 }}>
              <div style={{ position: "absolute", left: 7, top: 10, bottom: 10, width: 2, background: `linear-gradient(to bottom, ${C.blue}, ${C.teal})` }} />
              
              {historyModal.data.map((h, i) => (
                <div key={i} style={{ marginBottom: 30, position: "relative" }}>
                   <div style={{ 
                     position: "absolute", left: -22, top: 2, width: 12, height: 12, borderRadius: "50%", 
                     background: h.statut === "REVOQUE" ? C.red : C.green, border: `3px solid ${C.bg}`,
                     boxShadow: `0 0 10px ${h.statut === "REVOQUE" ? C.red : C.green}40`
                   }} />
                   <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: C.text }}>{h.statut === "REVOQUE" ? "🚨 Asset Revoked" : "🖋 Asset Committed"}</span>
                      <span style={{ fontSize: 11, color: C.textMut, fontFamily: C.mono }}>{h.timestamp}</span>
                   </div>
                   <div style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 10, padding: 14 }}>
                      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                         <div style={{ fontSize: 11, color: C.textSec }}><span style={{ fontWeight: 700 }}>TXID:</span> <code style={{ color: C.violet }}>{h.tx_id}</code></div>
                         <div style={{ fontSize: 11, color: C.textSec }}><span style={{ fontWeight: 700 }}>Data Hash:</span> <code style={{ color: C.teal }}>{h.hash_sha256}</code></div>
                      </div>
                   </div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 10, padding: 14, background: `${C.blue}10`, border: `1px solid ${C.blue}30`, borderRadius: 10, fontSize: 12, color: C.textSec, lineHeight: 1.5 }}>
               📌 <span style={{ fontWeight: 700, color: C.text }}>Auditor Note:</span> This trace is fetched directly from the Fabric <b>GetHistoryForKey</b> API, proving end-to-end immutability and provenance.
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
