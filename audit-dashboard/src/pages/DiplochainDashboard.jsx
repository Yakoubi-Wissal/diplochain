/**
 * DiplochainDashboard.jsx
 * ──────────────────────────────────────────────────────────────────────
 * Intégration dans audit-dashboard existant (port 3001)
 * Route : /blockchain  (configurer dans App.jsx / router.jsx)
 *
 * Connexion : fabric-api-server (port 4001)
 *   GET  /api/fabric/network/status   → état nœuds
 *   GET  /api/fabric/channels         → liste canaux
 *   GET  /api/fabric/transactions     → historique TX
 *   POST /api/fabric/channel/create   → créer canal
 *   POST /api/fabric/chaincode/invoke → invoquer chaincode
 *   GET  /api/fabric/reports/activity → données rapport
 * ──────────────────────────────────────────────────────────────────────
 */

import { useState, useEffect, useCallback, useRef } from "react";
import {
  useFabricNetwork,
  useFabricChannels,
  useFabricTransactions,
  useFabricLogs,
  useFabricStats
} from "../hooks/useFabric";
import {
  fabricApi,
  invokeChaincode,
  createChannel,
  generateReport,
  getFullProjectReport
} from "../services/fabricApi";

// ─── Palette tokens ───────────────────────────────────────────────────
const C = {
  bg:        "#07090F",
  surface:   "#0C1120",
  surfaceHi: "#111827",
  border:    "#1A2744",
  borderHi:  "#243660",
  blue:      "#3B82F6",
  teal:      "#0EA5E9",
  tealD:     "#0284C7",
  amber:     "#F59E0B",
  green:     "#22C55E",
  red:       "#EF4444",
  violet:    "#8B5CF6",
  text:      "#E2EAFF",
  textSec:   "#7A8FAD",
  textMut:   "#3D5070",
  mono:      "'JetBrains Mono', 'Fira Mono', monospace",
  sans:      "'Inter', system-ui, sans-serif",
};

// ─── Keyframes injectés une seule fois ───────────────────────────────
const STYLES = `
  @keyframes dc-fadeup  { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
  @keyframes dc-spin    { to { transform:rotate(360deg) } }
  @keyframes dc-pulse   { 0%,100%{opacity:1} 50%{opacity:.3} }
  @keyframes dc-blink   { 0%,100%{opacity:1} 49%{opacity:1} 50%{opacity:0} }
  @keyframes dc-slide   { from{opacity:0;transform:translateX(-4px)} to{opacity:1;transform:translateX(0)} }
  .dc-anim { animation: dc-fadeup .3s ease both }
  .dc-row:hover { background: ${C.surfaceHi} !important; transition: background .12s }
  .dc-btn { transition: filter .15s, transform .1s }
  .dc-btn:hover { filter: brightness(1.15) }
  .dc-btn:active { transform: scale(.97) }
`;

// ─── Primitives UI ────────────────────────────────────────────────────
const injectStyles = (() => {
  let injected = false;
  return () => {
    if (injected) return;
    const el = document.createElement("style");
    el.textContent = STYLES;
    document.head.appendChild(el);
    injected = true;
  };
})();

function Dot({ status }) {
  const map = { running: C.green, active: C.green, VALID: C.green, PENDING: C.amber, ERROR: C.red, stopped: C.red };
  const color = map[status] || C.textMut;
  return (
    <span style={{
      display: "inline-block", width: 8, height: 8, borderRadius: "50%",
      background: color, boxShadow: `0 0 6px ${color}`,
      animation: status === "PENDING" ? "dc-pulse 1.4s infinite" : "none",
      flexShrink: 0,
    }} />
  );
}

function Badge({ text, color = C.blue }) {
  return (
    <span style={{
      padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600,
      fontFamily: C.mono, background: `${color}20`, color,
      border: `1px solid ${color}40`, letterSpacing: ".02em", whiteSpace: "nowrap",
    }}>{text}</span>
  );
}

function Spinner({ size = 16 }) {
  return (
    <span style={{
      display: "inline-block", width: size, height: size,
      border: `2px solid currentColor`, borderTopColor: "transparent",
      borderRadius: "50%", animation: "dc-spin .7s linear infinite",
    }} />
  );
}

function DCButton({ children, onClick, variant = "primary", small, loading, disabled, icon }) {
  const styles = {
    primary: { bg: C.blue,    color: "#fff",       border: C.blue },
    teal:    { bg: C.teal,    color: "#fff",       border: C.teal },
    ghost:   { bg: "transparent", color: C.textSec, border: C.border },
    danger:  { bg: `${C.red}18`,  color: C.red,    border: `${C.red}50` },
    success: { bg: `${C.green}18`, color: C.green,  border: `${C.green}50` },
  };
  const s = styles[variant] || styles.primary;
  return (
    <button
      className="dc-btn"
      onClick={disabled || loading ? undefined : onClick}
      style={{
        display: "inline-flex", alignItems: "center", gap: 6,
        padding: small ? "5px 12px" : "8px 18px",
        background: s.bg, color: s.color,
        border: `1px solid ${s.border}`,
        borderRadius: 7, cursor: disabled ? "not-allowed" : "pointer",
        fontSize: small ? 12 : 13, fontWeight: 500, fontFamily: C.sans,
        opacity: disabled ? .5 : 1, whiteSpace: "nowrap",
      }}
    >
      {loading ? <Spinner size={13} /> : icon}
      {children}
    </button>
  );
}

function Card({ children, style = {}, delay = 0 }) {
  return (
    <div className="dc-anim" style={{
      background: C.surface, border: `1px solid ${C.border}`,
      borderRadius: 10, padding: "18px 20px",
      animationDelay: `${delay}ms`, ...style,
    }}>
      {children}
    </div>
  );
}

function SectionHead({ icon, title, sub, children }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18, gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 34, height: 34, borderRadius: 8,
          background: `${C.blue}18`, border: `1px solid ${C.blue}30`,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 16,
        }}>{icon}</div>
        <div>
          <div style={{ fontWeight: 600, fontSize: 15, color: C.text }}>{title}</div>
          {sub && <div style={{ fontSize: 12, color: C.textMut, marginTop: 1 }}>{sub}</div>}
        </div>
      </div>
      {children && <div style={{ display: "flex", gap: 8, alignItems: "center" }}>{children}</div>}
    </div>
  );
}

function StatCard({ label, value, sub, color = C.blue, icon, delay = 0 }) {
  return (
    <Card delay={delay} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 11, color: C.textMut, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>{label}</span>
        <span style={{ fontSize: 18 }}>{icon}</span>
      </div>
      <div style={{ fontSize: 30, fontWeight: 700, color: C.text, fontFamily: C.mono }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: C.textSec }}>{sub}</div>}
    </Card>
  );
}

// ─── Toasts ────────────────────────────────────────────────────────────
function Toast({ message, type = "success", onDone }) {
  useEffect(() => { const t = setTimeout(onDone, 3500); return () => clearTimeout(t); }, [onDone]);
  const colors = { success: C.green, error: C.red, info: C.blue, warning: C.amber };
  return (
    <div style={{
      position: "fixed", bottom: 24, right: 24, zIndex: 9999,
      background: C.surface, border: `1px solid ${colors[type]}`,
      borderRadius: 9, padding: "12px 18px", display: "flex", alignItems: "center", gap: 10,
      boxShadow: `0 8px 32px #0008`, animation: "dc-fadeup .3s ease",
      minWidth: 280, maxWidth: 400,
    }}>
      <Dot status={type === "success" ? "active" : type === "error" ? "ERROR" : "PENDING"} />
      <span style={{ fontSize: 13, color: C.text }}>{message}</span>
    </div>
  );
}

// ─── Tab : Réseau ────────────────────────────────────────────────────
function NetworkTab({ network, stats, channels, loading, onRefresh }) {
  if (loading) return (
    <div style={{ display: "flex", justifyContent: "center", padding: 60 }}>
      <Spinner size={28} />
    </div>
  );

  const nodes = network ? [
    { label: "Orderer",    name: network.orderer?.name || "orderer.diplochain.local", port: network.orderer?.port || 7050, status: network.orderer?.status || "running", detail: `Block height: ${network.orderer?.blockHeight ?? "—"}`, color: C.amber, icon: "⬡" },
    { label: "Peer0",      name: network.peer?.name || "peer0.diplochain.local",       port: network.peer?.port || 7051,   status: network.peer?.status || "running",   detail: `Endorsements: ${network.peer?.endorsements ?? "—"}`,    color: C.blue,  icon: "◉" },
    { label: "CouchDB",    name: network.couchdb?.name || "couchdb0.diplochain.local", port: network.couchdb?.port || 5984, status: network.couchdb?.status || "running", detail: `Docs: ${network.couchdb?.docs ?? "—"}`,                  color: C.teal,  icon: "◈" },
    { label: "Fabric CA",  name: network.ca?.name || "fabric-ca.diplochain.local",    port: network.ca?.port || 7054,     status: network.ca?.status || "running",     detail: "mTLS actif",                                               color: C.violet, icon: "◆" },
  ] : [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <StatCard label="Transactions" value={stats?.total_tx ?? "..."}  sub="+8 aujourd'hui"      icon="⬡" color={C.blue}   delay={0}   />
        <StatCard label="Canaux"       value={channels?.length ?? "..."}    sub="Nombre de réseaux isolés"    icon="◈" color={C.teal}   delay={50}  />
        <StatCard label="Diplômes"     value={stats?.diplomas ?? "..."}   sub="Inscrits sur la blockchain"     icon="◉" color={C.green}  delay={100} />
        <StatCard label="Statut"      value={network ? "ACTIF" : "OFFLINE"}    sub="Fabric v2.5.9"  icon="◆" color={network ? C.green : C.red}  delay={150} />
      </div>

      <Card>
        <SectionHead icon="🖧" title="Nœuds du réseau" sub="Hyperledger Fabric 2.5.9 · diplochain-net">
          <Dot status="active" />
          <span style={{ fontSize: 12, color: C.green, fontWeight: 600 }}>Réseau opérationnel</span>
          <DCButton variant="ghost" small onClick={onRefresh} icon="↺">Actualiser</DCButton>
        </SectionHead>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
          {nodes.map((n) => (
            <div key={n.name} style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "14px 16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                <div style={{ width: 28, height: 28, borderRadius: 6, background: `${n.color}18`, border: `1px solid ${n.color}30`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13 }}>{n.icon}</div>
                <span style={{ fontWeight: 600, fontSize: 13 }}>{n.label}</span>
                <Dot status={n.status} />
              </div>
              <div style={{ fontFamily: C.mono, fontSize: 10, color: C.textMut, marginBottom: 4, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{n.name}</div>
              <div style={{ fontSize: 11, color: C.textSec, marginBottom: 10 }}>{n.detail}</div>
              <div style={{ display: "flex", gap: 5 }}>
                <Badge text={`:${n.port}`} color={n.color} />
                <Badge text={n.status} color={C.green} />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

// ─── Tab : Canaux ─────────────────────────────────────────────────────
function ChannelsTab({ channels, loading, onCreated, onToast }) {
  const [showModal, setShowModal] = useState(false);
  const [institutionId, setInstitutionId] = useState("");
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    if (!institutionId) return;
    setCreating(true);
    try {
      await createChannel(institutionId);
      onToast(`Canal channel-${institutionId} créé et chaincode déployé !`, "success");
      setShowModal(false);
      setInstitutionId("");
      onCreated();
    } catch (e) {
      onToast(`Erreur : ${e.message}`, "error");
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div style={{ display: "flex", justifyContent: "center", padding: 60 }}><Spinner size={28} /></div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Card>
        <SectionHead icon="◈" title="Canaux Hyperledger Fabric" sub={`${(channels || []).length} canaux actifs — 1 institution = 1 canal isolé`}>
          <DCButton variant="teal" small onClick={() => setShowModal(true)} icon="+">Nouveau canal</DCButton>
        </SectionHead>

        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {/* En-tête table */}
          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 2fr 1fr 1fr 1fr auto", gap: 14, padding: "6px 14px" }}>
            {["Canal", "Institution", "Blocs", "TX", "Chaincode", "Statut"].map((h) => (
              <span key={h} style={{ fontSize: 11, color: C.textMut, fontWeight: 600, textTransform: "uppercase", letterSpacing: ".05em" }}>{h}</span>
            ))}
          </div>
          {(channels || []).map((ch, i) => (
            <div key={ch.id} className="dc-row dc-anim" style={{
              display: "grid", gridTemplateColumns: "1.2fr 2fr 1fr 1fr 1fr auto",
              alignItems: "center", gap: 14, padding: "12px 14px",
              background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8,
              animationDelay: `${i * 50}ms`,
            }}>
              <div>
                <div style={{ fontFamily: C.mono, fontSize: 13, fontWeight: 600, color: C.blue }}>{ch.id}</div>
                <div style={{ fontSize: 11, color: C.textMut, marginTop: 2 }}>id: {ch.institutionId}</div>
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{ch.institution}</div>
                <div style={{ fontSize: 11, color: C.textMut, marginTop: 2 }}>{ch.created}</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontFamily: C.mono, fontWeight: 700, color: C.teal, fontSize: 18 }}>{ch.height ?? "—"}</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontFamily: C.mono, fontWeight: 700, color: C.violet, fontSize: 18 }}>{ch.txCount ?? "—"}</div>
              </div>
              <Badge text={ch.chaincode || "diplochain v1.0"} color={C.amber} />
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <Dot status={ch.status || "active"} />
                <span style={{ fontSize: 11, color: C.green }}>actif</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Correspondance PostgreSQL */}
      <Card>
        <SectionHead icon="🔗" title="Liaison Canal ↔ PostgreSQL" sub="institution_blockchain_ext" />
        <div style={{ fontFamily: C.mono, fontSize: 12, lineHeight: 1.9, background: C.bg, padding: "14px 16px", borderRadius: 8, border: `1px solid ${C.border}`, overflowX: "auto" }}>
          <span style={{ color: C.textMut }}>-- Mise à jour après create-channel.sh</span><br />
          <span style={{ color: C.violet }}>UPDATE</span>
          <span style={{ color: C.text }}> institution_blockchain_ext</span><br />
          <span style={{ color: C.violet }}>SET</span>
          <span style={{ color: C.text }}> channel_id = </span>
          <span style={{ color: C.green }}>'channel-42'</span>
          <span style={{ color: C.text }}>,</span><br />
          <span style={{ color: C.text }}>    peer_node_url = </span>
          <span style={{ color: C.green }}>'grpc://peer0.diplochain.local:7051'</span><br />
          <span style={{ color: C.violet }}>WHERE</span>
          <span style={{ color: C.text }}> institution_id = </span>
          <span style={{ color: C.amber }}>42</span>
          <span style={{ color: C.text }}>;</span>
        </div>
      </Card>

      {/* Modal création canal */}
      {showModal && (
        <div style={{ position: "fixed", inset: 0, background: "#000c", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, animation: "dc-fadeup .2s ease" }}>
          <div style={{ background: C.surface, border: `1px solid ${C.borderHi}`, borderRadius: 12, padding: 28, width: 420, boxShadow: "0 20px 60px #0009" }}>
            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 6 }}>Créer un nouveau canal</div>
            <div style={{ fontSize: 12, color: C.textMut, marginBottom: 20 }}>
              Exécute <code style={{ background: C.bg, padding: "2px 6px", borderRadius: 4, color: C.blue, fontSize: 11 }}>./scripts/create-channel.sh &lt;id&gt;</code> via l'orchestrateur
            </div>
            <label style={{ fontSize: 12, color: C.textSec, display: "block", marginBottom: 6 }}>ID de l'institution</label>
            <input
              value={institutionId}
              onChange={(e) => setInstitutionId(e.target.value.replace(/\D/g, ""))}
              placeholder="ex: 5"
              autoFocus
              style={{ width: "100%", padding: "10px 14px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 7, color: C.text, fontSize: 14, fontFamily: C.mono, outline: "none", marginBottom: 10 }}
            />
            {institutionId && (
              <div style={{ fontSize: 12, color: C.textSec, marginBottom: 16 }}>
                Canal créé : <span style={{ color: C.blue, fontFamily: "monospace" }}>channel-{institutionId}</span>
              </div>
            )}
            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
              <DCButton variant="ghost" onClick={() => setShowModal(false)}>Annuler</DCButton>
              <DCButton variant="teal" onClick={handleCreate} loading={creating} disabled={!institutionId} icon="+">Créer le canal</DCButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Tab : Transactions ────────────────────────────────────────────────
const TYPE_COLORS = { RegisterDiploma: C.blue, VerifyDiploma: C.teal, RevokeDiploma: C.red, QueryDiploma: C.violet };

function TransactionsTab({ transactions, loading, onToast }) {
  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ fn: "RegisterDiploma", channel: "channel-1", diplomeId: "", hash: "", ipfsCid: "", institutionId: "1", etudiantId: "", date: new Date().toISOString().slice(0, 10) });
  const [invoking, setInvoking] = useState(false);
  const [result, setResult] = useState(null);

  const types = ["ALL", "RegisterDiploma", "VerifyDiploma", "RevokeDiploma", "QueryDiploma"];
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
      onToast(`Transaction ${form.fn} commitée — block ${res.block}`, "success");
    } catch (e) {
      setResult({ ok: false, msg: e.message });
      onToast(`Erreur chaincode : ${e.message}`, "error");
    } finally {
      setInvoking(false);
    }
  };

  if (loading) return <div style={{ display: "flex", justifyContent: "center", padding: 60 }}><Spinner size={28} /></div>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Card>
        <SectionHead icon="⚡" title="Transactions on-chain" sub={`${(transactions || []).length} transactions · toutes chaînes`}>
          <DCButton variant="teal" small onClick={() => setShowModal(true)} icon="⚡">Invoquer chaincode</DCButton>
        </SectionHead>

        {/* Filtres */}
        <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap", alignItems: "center" }}>
          {types.map((t) => (
            <button key={t} onClick={() => setFilter(t)} style={{
              padding: "4px 12px", borderRadius: 6, fontSize: 12, cursor: "pointer",
              background: filter === t ? `${TYPE_COLORS[t] || C.blue}20` : "transparent",
              color: filter === t ? (TYPE_COLORS[t] || C.blue) : C.textSec,
              border: `1px solid ${filter === t ? `${TYPE_COLORS[t] || C.blue}50` : C.border}`,
              fontFamily: C.sans, transition: "all .15s",
            }}>{t}</button>
          ))}
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher TX, étudiant, canal..."
            style={{ marginLeft: "auto", padding: "5px 12px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, color: C.text, fontSize: 12, outline: "none", width: 260 }}
          />
        </div>

        {/* Table */}
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${C.border}` }}>
                {["Type", "TX ID", "Canal", "Étudiant", "Statut", "Bloc", "Horodatage"].map((h) => (
                  <th key={h} style={{ padding: "7px 12px", textAlign: "left", fontSize: 11, fontWeight: 600, color: C.textMut, textTransform: "uppercase", letterSpacing: ".05em", whiteSpace: "nowrap" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((tx, i) => (
                <tr key={tx.txId || i} className="dc-row" style={{ borderBottom: `1px solid ${C.border}18`, cursor: "default" }}>
                  <td style={{ padding: "10px 12px", whiteSpace: "nowrap" }}><Badge text={tx.type} color={TYPE_COLORS[tx.type] || C.textSec} /></td>
                  <td style={{ padding: "10px 12px" }}><span style={{ fontFamily: C.mono, fontSize: 11, color: C.textSec }}>{(tx.txId || "").slice(0, 28)}…</span></td>
                  <td style={{ padding: "10px 12px" }}><Badge text={tx.channel} color={C.blue} /></td>
                  <td style={{ padding: "10px 12px", fontSize: 13, whiteSpace: "nowrap" }}>{tx.student}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <Dot status={tx.status} />
                      <span style={{ fontSize: 12, color: tx.status === "VALID" ? C.green : C.amber }}>{tx.status}</span>
                    </div>
                  </td>
                  <td style={{ padding: "10px 12px" }}><span style={{ fontFamily: C.mono, fontSize: 12, color: tx.block ? C.teal : C.amber }}>{tx.block ?? "—"}</span></td>
                  <td style={{ padding: "10px 12px", fontSize: 11, color: C.textMut, whiteSpace: "nowrap" }}>{tx.timestamp}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={7} style={{ padding: "40px 12px", textAlign: "center", color: C.textMut, fontSize: 13 }}>Aucune transaction</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Modal invoke */}
      {showModal && (
        <div style={{ position: "fixed", inset: 0, background: "#000c", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, animation: "dc-fadeup .2s ease" }}>
          <div style={{ background: C.surface, border: `1px solid ${C.borderHi}`, borderRadius: 12, padding: 28, width: 520, maxHeight: "88vh", overflowY: "auto", boxShadow: "0 20px 60px #0009" }}>
            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 6 }}>Invoquer le chaincode</div>
            <div style={{ fontSize: 12, color: C.textMut, marginBottom: 20 }}>Appel vers <code style={{ background: C.bg, padding: "2px 6px", borderRadius: 4, color: C.blue }}>POST /api/fabric/chaincode/invoke</code></div>

            {[
              { label: "Fonction", key: "fn", type: "select", opts: ["RegisterDiploma", "QueryDiploma", "VerifyDiploma", "RevokeDiploma", "QueryByInstitution"] },
              { label: "Canal", key: "channel", type: "select", opts: ["channel-1", "channel-2", "channel-42"] },
              { label: "Diplôme ID", key: "diplomeId", placeholder: "1" },
              { label: "Hash SHA-256 (64 chars)", key: "hash", placeholder: "a665a45920422f9d417e4867..." },
              { label: "IPFS CID", key: "ipfsCid", placeholder: "QmXf1eRH8nbV7sSzF..." },
              { label: "Institution ID", key: "institutionId", placeholder: "1" },
              { label: "Étudiant ID", key: "etudiantId", placeholder: "42" },
              { label: "Date émission", key: "date", placeholder: "2026-03-18" },
            ].map((f) => (
              <div key={f.key} style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, color: C.textSec, display: "block", marginBottom: 4 }}>{f.label}</label>
                {f.type === "select" ? (
                  <select value={form[f.key]} onChange={(e) => setForm((p) => ({ ...p, [f.key]: e.target.value }))}
                    style={{ width: "100%", padding: "8px 12px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, color: C.text, fontSize: 13, fontFamily: C.mono, outline: "none" }}>
                    {f.opts.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : (
                  <input value={form[f.key]} onChange={(e) => setForm((p) => ({ ...p, [f.key]: e.target.value }))} placeholder={f.placeholder}
                    style={{ width: "100%", padding: "8px 12px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, color: C.text, fontSize: 13, fontFamily: C.mono, outline: "none" }} />
                )}
              </div>
            ))}

            {result && (
              <div style={{ padding: "12px 14px", background: result.ok ? `${C.green}18` : `${C.red}18`, border: `1px solid ${result.ok ? C.green : C.red}40`, borderRadius: 8, marginBottom: 14 }}>
                {result.ok ? (
                  <>
                    <div style={{ fontSize: 13, color: C.green, fontWeight: 600 }}>✓ Transaction commitée</div>
                    <div style={{ fontSize: 11, fontFamily: "monospace", color: C.textMut, marginTop: 4 }}>TX: {result.txId}</div>
                    <div style={{ fontSize: 11, color: C.textMut }}>Block: {result.block}</div>
                  </>
                ) : (
                  <div style={{ fontSize: 13, color: C.red }}>✗ {result.msg}</div>
                )}
              </div>
            )}

            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
              <DCButton variant="ghost" onClick={() => { setShowModal(false); setResult(null); }}>Fermer</DCButton>
              <DCButton variant="teal" onClick={handleInvoke} loading={invoking} icon="⚡">Invoquer</DCButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Tab : Logs ────────────────────────────────────────────────────────
function LogsTab({ logs: initLogs }) {
  const [live, setLive] = useState(true);
  const [logs, setLogs] = useState(initLogs || []);
  const bottomRef = useRef(null);
  const LEVEL_COLORS = { INFO: C.teal, WARN: C.amber, ERROR: C.red };
  const EXTRA_LOGS = [
    { level: "INFO", src: "orderer",        msg: "Block committed on channel-1 height=%N" },
    { level: "INFO", src: "peer0",          msg: "Endorsement request received channel=%C" },
    { level: "INFO", src: "blockchain-svc", msg: "RegisterDiploma TX submitted" },
    { level: "WARN", src: "retry-worker",   msg: "PENDING diploma retry attempt %N/5" },
    { level: "INFO", src: "peer0",          msg: "Gossip: membership updated peers=1" },
  ];

  useEffect(() => {
    if (!live) return;
    const id = setInterval(() => {
      const tpl = EXTRA_LOGS[Math.floor(Math.random() * EXTRA_LOGS.length)];
      const msg = tpl.msg.replace("%N", Math.floor(Math.random() * 200)).replace("%C", "channel-1");
      setLogs((prev) => [...prev.slice(-99), { t: new Date().toISOString(), level: tpl.level, src: tpl.src, msg }]);
    }, 2800);
    return () => clearInterval(id);
  }, [live]);

  useEffect(() => {
    if (live && bottomRef.current) bottomRef.current.scrollIntoView({ behavior: "smooth" });
  }, [logs, live]);

  return (
    <Card>
      <SectionHead icon="⬛" title="Logs Fabric temps réel" sub="orderer · peer0 · blockchain-svc · retry-worker">
        <div style={{ display: "flex", gap: 6 }}>
          {Object.entries(LEVEL_COLORS).map(([l, c]) => (
            <span key={l} style={{ padding: "2px 8px", borderRadius: 4, fontSize: 11, background: `${c}18`, color: c, border: `1px solid ${c}40`, fontWeight: 600 }}>{l}</span>
          ))}
        </div>
        <DCButton variant={live ? "danger" : "success"} small onClick={() => setLive((v) => !v)}>
          {live ? "⏸ Pause" : "▶ Reprendre"}
        </DCButton>
      </SectionHead>

      <div style={{ background: C.bg, borderRadius: 8, border: `1px solid ${C.border}`, height: 380, overflowY: "auto", padding: "8px 0", fontFamily: C.mono, fontSize: 12, lineHeight: 1.7 }}>
        {logs.map((log, i) => (
          <div key={i} className="dc-row" style={{ padding: "2px 14px", display: "flex", gap: 12, animation: i === logs.length - 1 ? "dc-slide .2s ease" : "none" }}>
            <span style={{ color: C.textMut, minWidth: 90, flexShrink: 0 }}>{log.t?.slice(11, 23) || ""}</span>
            <span style={{ color: LEVEL_COLORS[log.level] || C.textSec, minWidth: 44, fontWeight: 600 }}>{log.level}</span>
            <span style={{ color: C.violet, minWidth: 110, flexShrink: 0 }}>[{log.src}]</span>
            <span style={{ color: C.textSec }}>{log.msg}</span>
          </div>
        ))}
        {live && <div style={{ padding: "4px 14px", color: C.textMut }}><span style={{ animation: "dc-blink 1s infinite" }}>█</span></div>}
        <div ref={bottomRef} />
      </div>
    </Card>
  );
}

// ─── Tab : Rapport ─────────────────────────────────────────────────────
function ReportsTab({ onToast, stats }) {
  const [loading, setLoading] = useState(null);
  const [done, setDone] = useState({});

  const REPORTS = [
    { id: "activity",     label: "Rapport d'activité",  desc: "Transactions, blocs, statuts · toutes chaînes", color: C.blue },
    { id: "diplomes",     label: "Diplômes émis",        desc: "TX_ID, hash SHA-256, CID IPFS",                color: C.teal },
    { id: "institutions", label: "Institutions & Canaux",desc: "institution ↔ channel_id ↔ peer_node_url",    color: C.violet },
    { id: "security",     label: "Audit de sécurité",    desc: "Révocations, tentatives invalides, certs",     color: C.amber },
  ];

  const generate = async (id, fmt) => {
    const key = `${id}_${fmt}`;
    setLoading(key);
    try {
      const data = await generateReport(id, fmt);
      if (fmt === "json") {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a"); a.href = url; a.download = `diplochain_${id}.json`; a.click();
        URL.revokeObjectURL(url);
      }
      setDone((p) => ({ ...p, [key]: true }));
      onToast(`Rapport ${id} exporté en ${fmt.toUpperCase()}`, "success");
    } catch (e) {
      onToast(`Erreur génération rapport : ${e.message}`, "error");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <StatCard label="Total TX"       value={stats?.total_tx ?? "..."}  sub="toutes chaînes"       icon="⬡" color={C.blue}  delay={0}   />
        <StatCard label="Diplômes émis"  value={stats?.diplomas ?? "..."}   sub="RegisterDiploma"       icon="◉" color={C.green} delay={50}  />
        <StatCard label="Vérifications"  value={stats?.verifications ?? "..."}   sub="VerifyDiploma"          icon="◈" color={C.teal}  delay={100} />
        <StatCard label="Révocations"    value={stats?.revocations ?? "..."}    sub="RevokeDiploma"          icon="◆" color={C.red}   delay={150} />
      </div>

      <Card>
        <SectionHead icon="📄" title="Génération de rapports" sub="Export PDF / JSON des activités blockchain" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 14 }}>
          {REPORTS.map((r) => (
            <div key={r.id} style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "14px 16px", display: "flex", gap: 14, alignItems: "flex-start" }}>
              <div style={{ width: 34, height: 34, borderRadius: 7, background: `${r.color}18`, border: `1px solid ${r.color}30`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, flexShrink: 0 }}>📊</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 3 }}>{r.label}</div>
                <div style={{ fontSize: 12, color: C.textMut, marginBottom: 12 }}>{r.desc}</div>
                <div style={{ display: "flex", gap: 8 }}>
                  <DCButton variant="ghost" small icon="⬇" onClick={() => generate(r.id, "json")} loading={loading === `${r.id}_json`}>
                    {done[`${r.id}_json`] ? "✓ JSON" : "Export JSON"}
                  </DCButton>
                  <DCButton variant="ghost" small icon="📄" onClick={() => generate(r.id, "pdf")} loading={loading === `${r.id}_pdf`}>
                    {done[`${r.id}_pdf`] ? "✓ PDF" : "Export PDF"}
                  </DCButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Aperçu JSON */}
      <Card>
        <SectionHead icon="{}" title="Structure JSON — GET /api/fabric/reports/activity" />
        <pre style={{ fontFamily: C.mono, fontSize: 11.5, lineHeight: 1.8, color: C.textSec, background: C.bg, padding: "14px 16px", borderRadius: 8, border: `1px solid ${C.border}`, overflowX: "auto", margin: 0, whiteSpace: "pre-wrap" }}>
{`{
  "report": "DiploChain Activity Report",
  "generated": "${new Date().toISOString()}",
  "network": {
    "orderer": "orderer.diplochain.local:7050",
    "peer": "peer0.diplochain.local:7051",
    "fabric_version": "2.5.9"
  },
  "summary": {
    "totalTransactions": 142,
    "diplomes": 89,
    "verifications": 34,
    "revocations": 4,
    "pendingBlockchain": 1,
    "channels": 3
  },
  "channels": [
    { "id": "channel-1", "institution": "Université de Tunis", "height": 87, "txCount": 54 },
    { "id": "channel-2", "institution": "ESPRIT", "height": 34, "txCount": 21 }
  ]
}`}
        </pre>
      </Card>
    </div>
  );
}


// ─── Tab : SmartDashboard ──────────────────────────────────────────────
function SmartDashboardTab({ network, loading, stats, transactions, onToast }) {
  const [logMessages, setLogMessages] = useState([]);
  const addLog = (msg, type="info") => setLogMessages(prev => [{ t: new Date().toLocaleTimeString(), msg, type }, ...prev].slice(0,10));

  const handleAction = async (actionFn, name) => {
    addLog(`Démarrage de l'action: ${name}`, "info");
    try {
      const res = await actionFn();
      addLog(`Succès: ${name} -> ${JSON.stringify(res)}`, "success");
      onToast(`${name} réussie`, "success");
    } catch(err) {
      addLog(`Erreur: ${name} -> ${err.message}`, "error");
      onToast(`Erreur: ${err.message}`, "error");
    }
  };

  const handleReport = async (type, format = "json") => {
    try {
      addLog(`Génération du rapport ${type}...`, "info");
      if (type === "project") {
        const data = await fabricApi.getFullProjectReport();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement("a"); a.href=url; a.download="report_full_project.json"; a.click();
        addLog("Rapport complet exporté", "success");
      } else {
        await fabricApi.generateReport(type, format);
        addLog(`Rapport ${type} [${format}] généré`, "success");
      }
    } catch (e) {
      addLog(`Erreur rapport: ${e.message}`, "error");
    }
  };

  const isApiOnline = network ? true : !loading && !!network;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <SectionHead icon="🚀" title="Smart Dashboard" sub="Console centrale de contrôle Fabric" />
      
      {/* System Status */}
      {/* System Status Dynamic */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        <StatCard label="Total Transactions" value={stats?.total_tx ?? "..."} icon="⚡" color={C.blue} sub="Total on-chain" />
        <StatCard label="Diplômes émis" value={stats?.diplomas ?? "..."} icon="📜" color={C.green} sub="Certifiés Fabric" />
        <StatCard label="Vérifications" value={stats?.verifications ?? "..."} icon="✅" color={C.teal} sub="Audit en cours" />
        <StatCard label="Révocations" value={stats?.revocations ?? "..."} icon="🚫" color={C.red} sub="Diplômes invalidés" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <Card>
          <div style={{ fontWeight: 600, marginBottom: 16 }}>Actions Rapides Blockchain</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <DCButton variant="blue" onClick={() => handleAction(() => fabricApi.loginAdmin(), "Login API")}>1. Login API</DCButton>
            <DCButton variant="teal" onClick={() => handleAction(() => fabricApi.createStudent({nom: "Audit", prenom: "Student", email_etudiant: `audit_${Date.now()}@test.com` }), "Create Student")}>2. Create Student</DCButton>
            <DCButton variant="teal" onClick={() => handleAction(() => fabricApi.createInstitution({nom_institution: "Audit University", type: "UNIVERSITE" }), "Create Institution")}>3. Create Institution</DCButton>
            <DCButton variant="success" onClick={() => handleAction(() => fabricApi.invokeChaincode({fn: "RegisterDiploma", channel: "channel-1", diplomeId: "D-999", hash: "4A2D35A3E0C1F78D9B4A2D35A3E0C1F78D9B4A2D35A3E0C1F78D9B4A2D35A3E0", ipfsCid: "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco", institutionId: "1", etudiantId: "1", date: "2026-03-23" }), "Issue Diploma")}>4. Issue Diploma (Demo)</DCButton>
            <DCButton variant="violet" onClick={() => handleAction(() => fabricApi.invokeChaincode({fn: "VerifyDiploma", channel: "channel-1", diplomeId: "D-999", hash: "4A2D35A3E0C1F78D9B4A2D35A3E0C1F78D9B4A2D35A3E0C1F78D9B4A2D35A3E0" }), "Verify Diploma")}>5. Verify Diploma (Demo)</DCButton>
          </div>
        </Card>

        <Card>
          <SectionHead icon="📊" title="Génération de Rapports" sub="Audit réel de la blockchain" />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 16 }}>
            <DCButton variant="ghost" small onClick={() => handleReport("activity", "json")}>Activity.json</DCButton>
            <DCButton variant="ghost" small onClick={() => handleReport("activity", "pdf")}>Activity.pdf</DCButton>
          </div>
          <DCButton variant="teal" icon="📄" onClick={() => handleReport("project", "json")}>Rapport Complet (.json)</DCButton>
        </Card>

        <Card>
          <div style={{ fontWeight: 600, marginBottom: 16 }}>Résultats & Logs Live</div>
          <div style={{ background: C.bg, borderRadius: 8, padding: 12, height: 260, overflowY: "auto", fontFamily: C.mono, fontSize: 11 }}>
            {logMessages.map((L, i) => (
              <div key={i} style={{ marginBottom: 6, color: L.type==="success"?C.green : L.type==="error"?C.red : C.textSec }}>
                [{L.t}] {L.msg}
              </div>
            ))}
            {logMessages.length === 0 && <div style={{color:C.textMut}}>Aucun log récent.</div>}
          </div>
        </Card>
      </div>
    </div>
  );
}

// ─── Composant principal ──────────────────────────────────────────────

export default function DiplochainDashboard() {
  injectStyles();

  const [activeTab, setActiveTab] = useState("smart");
  const [toast, setToast] = useState(null);
  const showToast = useCallback((message, type = "info") => setToast({ message, type }), []);

  const { data: network, loading: netLoading, refresh: netRefresh } = useFabricNetwork();
  const { data: channels, loading: chLoading, refresh: chRefresh } = useFabricChannels();
  const { data: transactions, loading: txLoading } = useFabricTransactions();
  const { data: stats } = useFabricStats();
  const { logs } = useFabricLogs();

  
  const TABS = [
    { id: "smart",        label: "Smart Dashboard", icon: "🚀" },
    { id: "network",      label: "Réseau",         icon: "🖧" },

    { id: "channels",     label: "Canaux",          icon: "◈" },
    { id: "transactions", label: "Transactions",    icon: "⚡" },
    { id: "logs",         label: "Logs",            icon: "⬛" },
    { id: "reports",      label: "Rapports",        icon: "📄" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: C.sans, fontSize: 14 }}>

      {/* Header */}
      <div style={{ background: C.surface, borderBottom: `1px solid ${C.border}`, padding: "14px 28px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 36, height: 36, borderRadius: 9, background: `linear-gradient(135deg, ${C.blue}, ${C.teal})`, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 16, color: "#fff" }}>D</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, letterSpacing: "-.01em" }}>DiploChain Dashboard</div>
            <div style={{ fontSize: 12, color: C.textMut }}>Hyperledger Fabric 2.5.9 · fabric-api-server:4001</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <DCButton variant="ghost" small onClick={() => window.location.href = '/audit-dashboard'} icon="←">Back to Audit</DCButton>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <Dot status="active" />
            <span style={{ fontSize: 12, color: C.green, fontWeight: 500 }}>Réseau actif</span>
          </div>
          <DCButton variant="ghost" small onClick={() => { netRefresh(); chRefresh(); }} icon="↺">Actualiser</DCButton>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ background: C.surface, borderBottom: `1px solid ${C.border}`, padding: "0 28px", display: "flex", gap: 2 }}>
        {TABS.map((tab) => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
            padding: "12px 18px", cursor: "pointer", fontSize: 13, fontWeight: activeTab === tab.id ? 600 : 400,
            color: activeTab === tab.id ? C.blue : C.textSec,
            background: "transparent", border: "none",
            borderBottom: `2px solid ${activeTab === tab.id ? C.blue : "transparent"}`,
            fontFamily: C.sans, display: "flex", alignItems: "center", gap: 7,
            transition: "all .15s",
          }}>
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Contenu */}
      <div style={{ padding: "24px 28px", maxWidth: 1200, margin: "0 auto" }}>
        
        {activeTab === "smart"        && <SmartDashboardTab network={network} loading={netLoading} stats={stats} transactions={transactions} onToast={showToast} />}
        {activeTab === "network"      && <NetworkTab      network={network} stats={stats} channels={channels} loading={netLoading} onRefresh={netRefresh} />}

        {activeTab === "channels"     && <ChannelsTab     channels={channels}       loading={chLoading}   onCreated={chRefresh}  onToast={showToast} />}
        {activeTab === "transactions" && <TransactionsTab transactions={transactions} loading={txLoading}  onToast={showToast} />}
        {activeTab === "logs"         && <LogsTab          logs={logs} />}
        {activeTab === "reports"      && <ReportsTab       onToast={showToast} stats={stats} />}
      </div>

      {/* Toast notification */}
      {toast && <Toast message={toast.message} type={toast.type} onDone={() => setToast(null)} />}
    </div>
  );
}
