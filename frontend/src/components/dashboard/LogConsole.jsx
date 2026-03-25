import React, { useState, useEffect, useRef } from 'react';
import { C } from './DashboardTokens';
import { Card, DCButton, Dot } from './UIPrimitives';
import { getLogs } from '../../services/fabricApi';

export default function LogConsole({ initialLogs = [] }) {
  const [live, setLive] = useState(true);
  const [logs, setLogs] = useState(initialLogs);
  const bottomRef = useRef(null);
  const LEVEL_COLORS = { INFO: C.teal, WARN: C.amber, ERROR: C.red, DEBU: C.violet };

  const fetchLogs = async () => {
     try {
       const newLogs = await getLogs(40);
       setLogs(newLogs);
     } catch(e) {/* ignore */}
  };

  useEffect(() => {
    if (!live) return;
    fetchLogs();
    const id = setInterval(fetchLogs, 5000);
    return () => clearInterval(id);
  }, [live]);

  useEffect(() => {
    if (live && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, live]);

  return (
    <Card icon="⬛" title="Fabric Node Logs (Docker)" action={
      <div style={{ display: "flex", gap: 8 }}>
        <DCButton variant={live ? "danger" : "success"} small onClick={() => setLive(!live)} icon={live ? "⏸" : "▶"}>
          {live ? "Pause" : "Resume"}
        </DCButton>
      </div>
    }>
      <div style={{ 
        background: "#000a", height: 420, borderRadius: 12, border: `1px solid ${C.border}`,
        padding: "12px 0", overflowY: "auto", fontFamily: C.mono, fontSize: 12, lineHeight: 1.8,
        display: "flex", flexDirection: "column"
      }}>
        {logs.map((log, i) => (
          <div key={i} className="dc-row" style={{ 
            padding: "2px 18px", display: "flex", gap: 14, 
            animation: i === logs.length - 1 ? "dc-fadein 0.2s ease" : "none" 
          }}>
            <span style={{ color: C.textMut, minWidth: 100, flexShrink: 0 }}>{log.t?.slice(11, 23) || "00:00:00.000"}</span>
            <span style={{ color: LEVEL_COLORS[log.level] || C.textSec, minWidth: 44, fontWeight: 700 }}>{log.level}</span>
            <span style={{ color: C.violet, minWidth: 80, flexShrink: 0, fontWeight: 600 }}>[{log.src}]</span>
            <span style={{ color: C.textSec, wordBreak: "break-all" }}>{log.msg}</span>
          </div>
        ))}
        {live && (
          <div style={{ padding: "4px 18px", color: C.textMut, fontSize: 13 }}>
             <span style={{ animation: "dc-blink 1s infinite" }}>█</span>
             <span style={{ marginLeft: 8, fontSize: 11, fontStyle: "italic" }}>Awaiting next block commit...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      
      <div style={{ marginTop: 14, display: "flex", gap: 12 }}>
         {Object.entries(LEVEL_COLORS).map(([l, c]) => (
           <div key={l} style={{ display: "flex", alignItems: "center", gap: 6 }}>
             <div style={{ width: 8, height: 8, borderRadius: "50%", background: c }} />
             <span style={{ fontSize: 11, color: C.textSec, fontWeight: 600 }}>{l}</span>
           </div>
         ))}
      </div>
    </Card>
  );
}
