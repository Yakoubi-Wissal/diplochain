import React, { useState } from 'react';
import { C } from './DashboardTokens';
import { Card, Badge, Dot, DCButton, Spinner } from './UIPrimitives';
import { createChannel } from '../../services/fabricApi';

export default function ChannelList({ channels, loading, onCreated, onToast }) {
  const [showModal, setShowModal] = useState(false);
  const [institutionId, setInstitutionId] = useState("");
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    if (!institutionId) return;
    setCreating(true);
    try {
      await createChannel(institutionId);
      onToast(`Channel created and chaincode deployed: channel-${institutionId}`, "success");
      setShowModal(false);
      setInstitutionId("");
      onCreated();
    } catch (e) {
      onToast(`Provisioning Error: ${e.message}`, "error");
    } finally {
      setCreating(false);
    }
  };

  if (loading && !channels) return <div style={{ textAlign: "center", padding: 60 }}><Spinner size={32} /></div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Card icon="◈" title="Fabric Isolated Channels" action={
        <DCButton variant="teal" small onClick={() => setShowModal(true)} icon="+">Provision Channel</DCButton>
      }>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {channels?.map((ch, i) => (
            <div key={ch.id} className="dc-row" style={{
              display: "grid", gridTemplateColumns: "1.2fr 2fr 1fr 1fr 1fr auto",
              alignItems: "center", gap: 16, padding: "16px 20px",
              background: C.bg, border: `1px solid ${C.border}`, borderRadius: 12,
              animation: `dc-fadein 0.4s ${C.anim} both`, animationDelay: `${i * 80}ms`
            }}>
              <div>
                <div style={{ fontFamily: C.mono, fontSize: 13, fontWeight: 700, color: C.blue }}>{ch.id}</div>
                <div style={{ fontSize: 10, color: C.textMut, marginTop: 4 }}>ID: {ch.institutionId}</div>
              </div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: C.text }}>{ch.institution}</div>
                <div style={{ fontSize: 11, color: C.textSec, marginTop: 2 }}>Joined: {ch.created}</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontFamily: C.mono, fontWeight: 700, color: C.teal, fontSize: 16 }}>{ch.height ?? "—"}</div>
                <div style={{ fontSize: 9, color: C.textMut }}>BLOCKS</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontFamily: C.mono, fontWeight: 700, color: C.violet, fontSize: 16 }}>{ch.txCount ?? "—"}</div>
                <div style={{ fontSize: 9, color: C.textMut }}>TX COUNT</div>
              </div>
              <Badge text={ch.chaincode || "DECODED V1.0"} color={C.amber} outline />
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Dot status={ch.status || "active"} pulse={ch.status === "active"} />
                <span style={{ fontSize: 11, fontWeight: 700, color: C.green, textTransform: "uppercase" }}>Operational</span>
              </div>
            </div>
          ))}
          {(!channels || channels.length === 0) && (
            <div style={{ padding: 40, textAlign: "center", color: C.textMut }}>No isolated channels detected.</div>
          )}
        </div>
      </Card>

      <Card icon="🔗" title="Ledger-Database Synchronization" delay={200}>
        <div style={{ fontFamily: C.mono, fontSize: 11, lineHeight: 2, background: "#000a", padding: "18px 24px", borderRadius: 10, border: `1px solid ${C.border}`, overflowX: "auto" }}>
          <span style={{ color: C.textMut }}>// Oracle Bridge Trace after create-channel.sh</span><br />
          <span style={{ color: C.violet }}>UPDATE</span> <span style={{ color: C.text }}>institution_blockchain_ext</span><br />
          <span style={{ color: C.violet }}>SET</span> <span style={{ color: C.text }}>channel_id =</span> <span style={{ color: C.green }}>'channel-42'</span>,<br />
          <span style={{ color: C.text }}>    peer_node_url =</span> <span style={{ color: C.green }}>'grpc://peer0.diplochain.local:7051'</span><br />
          <span style={{ color: C.violet }}>WHERE</span> <span style={{ color: C.text }}>institution_id =</span> <span style={{ color: C.amber }}>42</span>;
        </div>
      </Card>

      {showModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", backdropFilter: "blur(8px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div style={{ background: C.surface, border: `1px solid ${C.borderHi}`, borderRadius: 16, padding: 32, width: 420, boxShadow: C.shadow }}>
            <div style={{ fontWeight: 700, fontSize: 18, color: C.text, marginBottom: 8 }}>Provision New Ledger Channel</div>
            <div style={{ fontSize: 12, color: C.textMut, marginBottom: 24 }}>
              Initializes genesis block and joins Peer0.
            </div>
            <label style={{ fontSize: 11, color: C.textSec, display: "block", marginBottom: 6, fontWeight: 700, textTransform: "uppercase" }}>Institution Mapping ID</label>
            <input
              value={institutionId}
              onChange={(e) => setInstitutionId(e.target.value.replace(/\D/g, ""))}
              placeholder="e.g. 5"
              autoFocus
              style={{ width: "100%", padding: "12px 16px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 10, color: C.text, fontSize: 14, fontFamily: C.mono, outline: "none", marginBottom: 12 }}
            />
            {institutionId && (
              <div style={{ fontSize: 12, color: C.blue, marginBottom: 20, fontWeight: 600 }}>
                Projected: <span style={{ fontFamily: C.mono }}>channel-{institutionId}</span>
              </div>
            )}
            <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
              <DCButton variant="ghost" onClick={() => setShowModal(false)}>Cancel</DCButton>
              <DCButton variant="teal" onClick={handleCreate} loading={creating} disabled={!institutionId} icon="+">Initialize</DCButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
