import React from 'react';
import { C } from './DashboardTokens';
import { Card, StatCard, DCButton, Badge } from './UIPrimitives';
import { fabricApi } from '../../services/fabricApi';

export default function SmartBoard({ stats, onToast, addLog, onRunAudit, auditRunning }) {
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
      // Fallback si pas de prop
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

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <StatCard label="Stability Score" value={stats?.stability_score ?? "98.2"} icon="🛡️" color={C.teal} sub="Project Health Index" trend={2.1} delay={0} />
        <StatCard label="Error Rate" value={stats?.error_rate ?? "0.42"} icon="⚠️" color={C.red} sub="Last 24 Hours (%)" trend={-15} delay={100} />
        <StatCard label="Avg Latency" value={stats?.avg_latency ?? "124"} icon="⏱️" color={C.blue} sub="Response Time (ms)" trend={-5} delay={200} />
        <StatCard label="Active Users" value={stats?.active_users ?? "12"} icon="👥" color={C.amber} sub="Real-time Monitoring" trend={8} delay={300} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <StatCard label="Total Ledgers" value={stats?.total_tx ?? "0"} icon="⚡" color={C.blue} sub="Total Transactions" trend={12} delay={400} />
        <StatCard label="Diplomes" value={stats?.diplomas ?? "0"} icon="📜" color={C.green} sub="Certified on Fabric" trend={5} delay={500} />
        <StatCard label="Verifications" value={stats?.verifications ?? "0"} icon="✅" color={C.teal} sub="Audit Validations" trend={24} delay={600} />
        <StatCard label="Revocations" value={stats?.revocations ?? "0"} icon="🚫" color={C.red} sub="Invalidated Assets" trend={-2} delay={700} />
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

        <Card icon="📊" title="Compliance Overview">
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
             {[
               { label: "GDPR Compliance", val: 98, color: C.green },
               { label: "Blockchain Integrity", val: 100, color: C.blue },
               { label: "Service Uptime", val: 99.4, color: C.teal },
               { label: "Audit Readiness", val: 85, color: C.amber },
             ].map((m, i) => (
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
               </div>
             ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
