import React from 'react';
import { C } from './DashboardTokens';
import { Card, Dot, Badge, DCButton } from './UIPrimitives';

export default function NetworkPanel({ network, stats, loading, onRefresh }) {
  const nodes = network ? [
    { label: "Orderer",    name: network.orderer?.name || "orderer.diplochain.local", port: network.orderer?.port || 7050, status: network.orderer?.status || "running", detail: `Block: ${network.orderer?.blockHeight ?? 142}`, color: C.amber, icon: "⬡" },
    { label: "Peer0",      name: network.peer?.name || "peer0.diplochain.local",       port: network.peer?.port || 7051,   status: network.peer?.status || "running",   detail: `TX: ${network.peer?.endorsements ?? 89}`,    color: C.blue,  icon: "◉" },
    { label: "CouchDB",    name: network.couchdb?.name || "couchdb0.diplochain.local", port: network.couchdb?.port || 5984, status: network.couchdb?.status || "running", detail: `Docs: ${network.couchdb?.docs ?? 237}`,                  color: C.teal,  icon: "◈" },
    { label: "Fabric CA",  name: network.ca?.name || "fabric-ca.diplochain.local",    port: network.ca?.port || 7054,     status: network.ca?.status || "running",     detail: "TLS: Active",                                               color: C.violet, icon: "◆" },
  ] : [];

  return (
    <Card icon="🖧" title="Fabric Network Nodes" action={
      <DCButton variant="ghost" small onClick={onRefresh} icon="↺">Sync</DCButton>
    }>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
        {nodes.map((n, i) => (
          <div key={n.name} style={{ 
            background: C.bg, border: `1px solid ${C.border}`, borderRadius: 12, padding: "16px 20px",
            animation: `dc-fadein 0.4s ${C.anim} both`, animationDelay: `${i * 100}ms`
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
              <div style={{ 
                width: 32, height: 32, borderRadius: 8, background: `${n.color}15`, 
                border: `1px solid ${n.color}30`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, color: n.color
              }}>{n.icon}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: C.text }}>{n.label}</div>
                <div style={{ fontSize: 11, color: C.textMut, fontFamily: C.mono, overflow: "hidden", textOverflow: "ellipsis" }}>{n.name}</div>
              </div>
              <Dot status={n.status} pulse={n.status === "running"} />
            </div>
            
            <div style={{ fontSize: 12, color: C.textSec, marginBottom: 16, fontWeight: 500 }}>{n.detail}</div>
            
            <div style={{ display: "flex", gap: 6 }}>
              <Badge text={`PORT:${n.port}`} color={n.color} outline />
              <Badge text={n.status} color={n.status === "running" ? C.green : C.red} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
