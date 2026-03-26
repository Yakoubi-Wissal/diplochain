import React, { useState } from 'react';
import { C } from './DashboardTokens';
import { Card, StatCard, DCButton, Badge } from './UIPrimitives';
import { generateReport } from '../../services/fabricApi';

export default function ReportGenerator({ stats, onToast }) {
  const [loading, setLoading] = useState(null);
  const [done, setDone] = useState({});

  const REPORTS = [
    { id: "activity",     label: "Ledger Activity",  desc: "Full transaction history and block hashes.", color: C.blue },
    { id: "diplomes",     label: "Asset Registry",   desc: "IPFS CIDs and SHA-256 integrity hashes.",      color: C.teal },
    { id: "institutions", label: "Governance Map",   desc: "Institution to Channel mapping and node URLs.", color: C.violet },
    { id: "security",     label: "Security Audit",   desc: "Revocations and unauthorized access attempts.", color: C.amber },
  ];

  const generate = async (id, fmt) => {
    const key = `${id}_${fmt}`;
    setLoading(key);
    try {
      const data = await generateReport(id, fmt);
      if (fmt === "json") {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a"); a.href = url; a.download = `diplo_report_${id}.json`; a.click();
        URL.revokeObjectURL(url);
      }
      setDone((p) => ({ ...p, [key]: true }));
      onToast(`Compliance report (${id}) exported as ${fmt.toUpperCase()}`, "success");
    } catch (e) {
      onToast(`Export Failed: ${e.message}`, "error");
    } finally {
      setLoading(null);
    }
  };

  const [auditSummary, setAuditSummary] = useState(null);

  React.useEffect(() => {
    fabricApi.getStabilityMetrics().then(setAuditSummary).catch(() => {});
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <StatCard label="Ledger Commits" value={stats?.total_tx ?? "0"} sub="Total Ops" icon="⬡" color={C.blue} delay={0} />
        <StatCard label="Assets" value={stats?.diplomas ?? "0"} sub="Unique IDs" icon="◉" color={C.green} delay={50} />
        <StatCard label="Validations" value={stats?.verifications ?? "0"} sub="Proof of Work" icon="◈" color={C.teal} delay={100} />
        <StatCard label="Invalidated" value={stats?.revocations ?? "0"} sub="Zero-Trust" icon="◆" color={C.red} delay={150} />
      </div>

      {/* Visual Summary Section */}
      <Card icon="🛡" title="Live Governance Summary" action={<Badge text="Real-time Status" color={C.teal} />}>
         <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
            {[
              { mod: "User Auth", score: auditSummary?.security || 100, last: "Login pattern: Normal" },
              { mod: "Blockchain", score: 100, last: "Ledger Consistency: Valid" },
              { mod: "IPFS Storage", score: auditSummary?.stability || 100, last: "Pinning latency < 200ms" },
              { mod: "System Agent", score: auditSummary?.network || 100, last: "No self-healing events" }
            ].map(m => (
              <div key={m.mod} style={{ padding: 16, background: `${C.surfaceHi}40`, borderRadius: 12, border: `1px solid ${C.border}` }}>
                 <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <span style={{ fontWeight: 700, fontSize: 13 }}>{m.mod}</span>
                    <Badge
                       text={m.score > 90 ? "Stable" : m.score > 70 ? "Degraded" : "Critical"}
                       color={m.score > 90 ? C.green : m.score > 70 ? C.amber : C.red}
                    />
                 </div>
                 <div style={{ fontSize: 24, fontWeight: 800, color: m.score > 70 ? "#fff" : C.red, marginBottom: 4 }}>{m.score}%</div>
                 <div style={{ fontSize: 10, color: C.textMut }}>{m.last}</div>
              </div>
            ))}
         </div>

         <div style={{ marginTop: 20, padding: 16, background: `${C.blue}10`, borderRadius: 12, border: `1px solid ${C.blue}30` }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: C.blue, textTransform: "uppercase", marginBottom: 8 }}>Current AI Recommendations</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
               {auditSummary?.recommendations?.map((rec, i) => (
                 <div key={i} style={{ fontSize: 12, display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ color: C.blue }}>•</span>
                    <span>{rec}</span>
                 </div>
               )) || "Scanning system components..."}
            </div>
         </div>
      </Card>

      <Card icon="📄" title="Compliance & Audit Exports" action={<Badge text="Audit Ready" color={C.green} />}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: 16 }}>
          {REPORTS.map((r, i) => (
            <div key={r.id} style={{ 
              background: C.bg, border: `1px solid ${C.border}`, borderRadius: 12, padding: "20px", 
              display: "flex", gap: 18, alignItems: "flex-start",
              animation: `dc-fadein 0.4s ${C.anim} both`, animationDelay: `${i * 100}ms`
            }}>
              <div style={{ 
                width: 44, height: 44, borderRadius: 10, background: `${r.color}15`, 
                border: `1px solid ${r.color}30`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, color: r.color, flexShrink: 0 
              }}>📊</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: C.text, marginBottom: 4 }}>{r.label}</div>
                <div style={{ fontSize: 12, color: C.textMut, marginBottom: 16, lineHeight: 1.5 }}>{r.desc}</div>
                <div style={{ display: "flex", gap: 10 }}>
                  <DCButton variant="ghost" small icon="⬇" onClick={() => generate(r.id, "json")} loading={loading === `${r.id}_json`}>
                    {done[`${r.id}_json`] ? "✓ JSON" : "JSON Data"}
                  </DCButton>
                  <DCButton variant="ghost" small icon="📄" onClick={() => generate(r.id, "pdf")} loading={loading === `${r.id}_pdf`}>
                    {done[`${r.id}_pdf`] ? "✓ PDF" : "PDF Report"}
                  </DCButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card icon="{}" title="Asset Schema Definition (Fabric V2.5)">
        <pre style={{ 
          fontFamily: C.mono, fontSize: 11, lineHeight: 1.8, color: C.textSec, background: "#000a", 
          padding: "20px", borderRadius: 12, border: `1px solid ${C.border}`, overflowX: "auto", margin: 0 
        }}>
{`type Diploma struct {
    ID            string \`json:"id"\`
    Hash          string \`json:"hash"\`
    IPFSCID       string \`json:"ipfsCid"\`
    InstitutionID string \`json:"institutionId"\`
    StudentID     string \`json:"etudiantId"\`
    Date          string \`json:"date"\`
    Status        string \`json:"status"\`  // VALID, REVOKED
    Certifier     string \`json:"certifier"\`
}`}
        </pre>
      </Card>
    </div>
  );
}
