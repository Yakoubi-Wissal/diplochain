import React, { useState, useCallback } from 'react';
import { 
  useFabricNetwork, 
  useFabricChannels, 
  useFabricTransactions, 
  useFabricStats,
  useStabilityStats,
  useStabilityHistory
} from '../hooks/useFabric';
import { C } from '../components/dashboard/DashboardTokens';
import { injectStyles, Dot, Toast } from '../components/dashboard/UIPrimitives';

// Modular Components
import SmartBoard from '../components/dashboard/SmartBoard';
import NetworkPanel from '../components/dashboard/NetworkPanel';
import ChannelList from '../components/dashboard/ChannelList';
import TransactionLedger from '../components/dashboard/TransactionLedger';
import LogConsole from '../components/dashboard/LogConsole';
import HealthMapper from '../components/dashboard/HealthMapper';
import ReportGenerator from '../components/dashboard/ReportGenerator';

export default function DiplochainDashboard() {
  injectStyles();

  const [activeTab, setActiveTab] = useState("smart");
  const [toast, setToast] = useState(null);
  const [logMessages, setLogMessages] = useState([]);

  const showToast = useCallback((message, type = "info") => setToast({ message, type }), []);
  const addLog = useCallback((msg, type = "info") => {
    setLogMessages(prev => [{ t: new Date().toISOString(), msg, level: type.toUpperCase(), src: "audit-ui" }, ...prev].slice(0, 50));
  }, []);

  // Data Hooks
  const { data: network, loading: netLoading, refresh: netRefresh } = useFabricNetwork();
  const { data: channels, loading: chLoading, refresh: chRefresh } = useFabricChannels();
  const { data: transactions, loading: txLoading } = useFabricTransactions();
  const { data: stats } = useFabricStats();
  const { data: stability } = useStabilityStats();
  const { data: history } = useStabilityHistory();

  const TABS = [
    { id: "smart",        label: "Smart Dashboard", icon: "🚀" },
    { id: "network",      label: "Node Topology",   icon: "🖧" },
    { id: "channels",     label: "Isolated Channels",icon: "◈" },
    { id: "transactions", label: "Ledger Explorer",  icon: "⚡" },
    { id: "health",       label: "System Health",   icon: "🗺" },
    { id: "logs",         label: "Real-time Logs",  icon: "⬛" },
    { id: "reports",      label: "Audit Reports",   icon: "📄" },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case "smart":        return <SmartBoard stats={stats} stability={stability} history={history} onToast={showToast} addLog={addLog} />;
      case "network":      return <NetworkPanel network={network} loading={netLoading} onRefresh={netRefresh} />;
      case "channels":     return <ChannelList channels={channels} loading={chLoading} onCreated={chRefresh} onToast={showToast} />;
      case "transactions": return <TransactionLedger transactions={transactions} loading={txLoading} onToast={showToast} />;
      case "health":       return <HealthMapper />;
      case "logs":         return <LogConsole initialLogs={logMessages} />;
      case "reports":      return <ReportGenerator stats={stats} onToast={showToast} />;
      default:             return null;
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: C.sans, fontSize: 14 }}>
      
      {/* Premium Header */}
      <div className="dc-glass" style={{ 
        position: "sticky", top: 0, zIndex: 100,
        padding: "16px 32px", display: "flex", alignItems: "center", justifyContent: "space-between",
        borderBottom: `1px solid ${C.border}`
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ 
            width: 42, height: 42, borderRadius: 12, background: C.blueG, 
            display: "flex", alignItems: "center", justifyContent: "center", 
            fontSize: 22, boxShadow: "0 0 20px rgba(59, 130, 246, 0.5)" 
          }}>⛓</div>
          <div>
            <div style={{ fontWeight: 800, fontSize: 18, letterSpacing: "-0.02em", color: "#fff" }}>DIPLOCHAIN <span style={{ color: C.blue }}>V2</span></div>
            <div style={{ fontSize: 11, color: C.textMut, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em" }}>Audit & Compliance Engine</div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <div style={{ display: "flex", gap: 16, alignItems: "center", padding: "6px 16px", background: "#0005", borderRadius: 30, border: `1px solid ${C.border}` }}>
             <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Dot status={network ? "active" : "down"} pulse />
                <span style={{ fontSize: 11, fontWeight: 700, color: network ? C.green : C.red }}>{network ? "FABRIC ONLINE" : "NETWORK OFFLINE"}</span>
             </div>
             <div style={{ width: 1, height: 14, background: C.border }} />
             <div style={{ fontSize: 11, color: C.textSec, fontWeight: 600 }}>v2.5.9-LTS</div>
          </div>
          <div style={{ width: 36, height: 36, borderRadius: "50%", background: C.surfaceHi, border: `1px solid ${C.border}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>👤</div>
        </div>
      </div>

      <div style={{ display: "flex", minHeight: "calc(100vh - 75px)" }}>
        
        {/* Sidebar Navigation */}
        <div style={{ 
          width: 260, borderRight: `1px solid ${C.border}`, padding: "24px 16px", 
          display: "flex", flexDirection: "column", gap: 4, background: `${C.surface}40` 
        }}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "12px 16px", borderRadius: 10, border: "none",
                background: activeTab === tab.id ? `${C.blue}15` : "transparent",
                color: activeTab === tab.id ? C.blue : C.textSec,
                cursor: "pointer", textAlign: "left", fontSize: 13, fontWeight: 600,
                transition: "all 0.2s ease",
              }}
            >
              <span style={{ fontSize: 16 }}>{tab.icon}</span>
              {tab.label}
              {activeTab === tab.id && <div style={{ marginLeft: "auto", width: 4, height: 4, borderRadius: "50%", background: C.blue }} />}
            </button>
          ))}
          
          <div style={{ marginTop: "auto", padding: 16, borderRadius: 12, background: `${C.surfaceHi}40`, border: `1px solid ${C.border}` }}>
             <div style={{ fontSize: 11, color: C.textMut, fontWeight: 700, textTransform: "uppercase", marginBottom: 8 }}>Internal Node Status</div>
             <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {["Orderer", "Peer0", "CouchDB"].map(n => (
                  <div key={n} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                     <span style={{ fontSize: 11, color: C.textSec }}>{n}</span>
                     <Dot status="active" />
                  </div>
                ))}
             </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div style={{ flex: 1, padding: "32px 40px", overflowY: "auto" }}>
          {renderContent()}
        </div>

      </div>

      {toast && <Toast message={toast.message} type={toast.type} onDone={() => setToast(null)} />}
    </div>
  );
}
