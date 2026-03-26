import React from 'react';
import { C } from './DashboardTokens';
import { Card, StatCard, DCButton, Badge } from './UIPrimitives';
import { fabricApi } from '../../services/fabricApi';

export default function SmartBoard({ stats, stability, history, onToast, addLog, onRunAudit, auditRunning }) {
  const handleAction = async (actionFn, name) => {
    addLog(`Initiating: ${name}`, "info");
    try {
      const res = await actionFn();
      addLog(`Success: ${name} -> ID: ${res.txId || res.institution_id || res.etudiant_id}`, "success");
      onToast(`${name} completed`, "success");
    } catch(err) {
      addLog(`Error: ${name} -> ${err.message}`, "error");
      onToast(`Error: ${err.message}`, "error");
    }
  };

  const handleFullAudit = async () => {
    if (onRunAudit) {
      onRunAudit();
    } else {
      addLog("Starting Full System Audit...", "info");
      try {
        const report = await fabricApi.getFullProjectReport();
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `diplo_audit_${new Date().toISOString().slice(0,10)}.json`;
        a.click();
        addLog("Full Project Audit Report generated and downloaded.", "success");
        onToast("Audit Report Ready", "success");
      } catch (e) {
        addLog(`Audit Failed: ${e.message}`, "error");
        onToast("Audit Failed", "error");
      }
    }
  };

  const stabilityItems = [
    { label: "System Stability", val: stability?.stability || 0, color: C.green, sub: "Based on 0 critical crashes" },
    { label: "Security Integrity", val: stability?.security || 0, color: C.blue, sub: `${100 - (stability?.security || 100)}% vulnerability risk` },
    { label: "Network Health", val: stability?.network || 0, color: C.teal, sub: "Latency < 50ms" },
    { label: "Anomaly Score", val: stability?.anomaly || 0, color: C.amber, sub: `${100 - (stability?.anomaly || 100)}% anomaly probability` },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <StatCard label="Total Ledgers" value={stats?.total_tx ?? "0"} icon="⚡" color={C.blue} sub="Total Transactions" trend={12} delay={0} />
        <StatCard label="Diplomes" value={stats?.diplomas ?? "0"} icon="📜" color={C.green} sub="Certified on Fabric" trend={5} delay={100} />
        <StatCard label="Verifications" value={stats?.verifications ?? "0"} icon="✅" color={C.teal} sub="Audit Validations" trend={24} delay={200} />
        <StatCard label="Revocations" value={stats?.revocations ?? "0"} icon="🚫" color={C.red} sub="Invalidated Assets" trend={-2} delay={300} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <Card icon="🚀" title="Quick Audit Actions" action={<Badge text="Admin Role" color={C.amber} />}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <DCButton variant="primary" small onClick={() => handleAction(() => fabricApi.loginAdmin(), "Admin Authentication")} icon="🔑" disabled={auditRunning}>1. Authenticate</DCButton>
            <DCButton variant="teal" small onClick={() => handleAction(() => fabricApi.createStudent({nom: "Audit", prenom: "Student", email_etudiant: `audit_${Date.now()}@test.com` }), "Mock Student Creation")} icon="👤" disabled={auditRunning}>2. Create Student</DCButton>
            <DCButton variant="teal" small onClick={() => handleAction(() => fabricApi.createInstitution({nom_institution: "Audit Academy", type: "UNIVERSITE" }), "Mock Inst. Creation")} icon="🏛" disabled={auditRunning}>3. Create Institution</DCButton>
            <DCButton variant="success" small onClick={() => handleAction(() => fabricApi.invokeChaincode({fn: "RegisterDiploma", channel: "channel-1", diplomeId: "AUDIT-" + Date.now().toString().slice(-4), hash: "HASH-"+Date.now(), ipfsCid: "Qm-AUDIT", institutionId: "1", etudiantId: "1", date: new Date().toISOString().slice(0,10) }), "Issue Demo Diploma")} icon="🖋" disabled={auditRunning}>4. Issue Asset</DCButton>
          </div>
          <div style={{ marginTop: 20, paddingTop: 20, borderTop: `1px solid ${C.border}` }}>
             <DCButton variant="primary" fullWidth onClick={handleFullAudit} icon={auditRunning ? null : "📋"} loading={auditRunning}>
               {auditRunning ? "Audit Engine Running..." : "Run Full Automated Audit Sequence"}
             </DCButton>
          </div>
        </Card>

        <Card icon="📊" title="Stability & Security Score" action={<Badge text="Real-time" color={C.teal} />}>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
             {stabilityItems.map((m, i) => (
               <div key={m.label}>
                 <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, fontSize: 12, fontWeight: 600 }}>
                   <span style={{ color: C.textSec }}>{m.label}</span>
                   <span style={{ color: m.color }}>{m.val}%</span>
                 </div>
                 <div style={{ height: 6, width: "100%", background: C.bg, borderRadius: 3, overflow: "hidden" }}>
                   <div style={{ 
                     height: "100%", width: `${m.val}%`, background: m.color, borderRadius: 3, 
                     boxShadow: `0 0 10px ${m.color}60`, transition: "width 1s ease",
                     animation: `dc-fadein 1s ${C.anim} both`, animationDelay: `${i * 150}ms`
                   }} />
                 </div>
                 <div style={{ fontSize: 10, color: C.textMut, marginTop: 4 }}>{m.sub}</div>
               </div>
             ))}
          </div>
          <div style={{ marginTop: 15, padding: 12, background: `${C.blue}10`, borderRadius: 8, border: `1px solid ${C.blue}30` }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: C.blue, textTransform: "uppercase", marginBottom: 5 }}>AI Recommendations</div>
            <div style={{ fontSize: 11, color: C.textSec }}>
                {stability?.recommendations?.map((r, idx) => (
                    <div key={idx}>• {r}</div>
                )) || "Fetching recommendations..."}
            </div>
          </div>
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 16 }}>
        <Card icon="📈" title="Historical Trends (Stability & Security)">
          <div style={{ height: 120, display: "flex", alignItems: "flex-end", gap: 8, padding: "10px 0" }}>
             {history?.map((h, i) => (
               <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                  <div style={{ width: "100%", display: "flex", gap: 2, height: 100, alignItems: "flex-end" }}>
                     <div style={{ flex: 1, height: `${h.stability}%`, background: C.green, opacity: 0.7, borderRadius: "2px 2px 0 0" }} />
                     <div style={{ flex: 1, height: `${h.security}%`, background: C.blue, opacity: 0.7, borderRadius: "2px 2px 0 0" }} />
                  </div>
                  <div style={{ fontSize: 9, color: C.textMut }}>{new Date(h.timestamp).getHours()}h</div>
               </div>
             ))}
             {(!history || history.length === 0) && <div style={{ width: "100%", textAlign: "center", color: C.textMut, fontSize: 12 }}>No historical data available</div>}
          </div>
          <div style={{ display: "flex", gap: 16, marginTop: 10 }}>
             <div style={{ display: "flex", alignItems: "center", gap: 4 }}><div style={{ width: 8, height: 8, background: C.green, borderRadius: 2 }} /><span style={{ fontSize: 10, color: C.textSec }}>Stability</span></div>
             <div style={{ display: "flex", alignItems: "center", gap: 4 }}><div style={{ width: 8, height: 8, background: C.blue, borderRadius: 2 }} /><span style={{ fontSize: 10, color: C.textSec }}>Security</span></div>
          </div>
        </Card>
      </div>
    </div>
  );
}
