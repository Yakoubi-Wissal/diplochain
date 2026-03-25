import React, { useState, useCallback, useEffect } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import axios from 'axios';

// Discovery & Stats Hooks
import { 
  useFabricNetwork, 
  useFabricChannels, 
  useFabricTransactions, 
  useFabricStats 
} from './hooks/useFabric';

// Service API
import { fabricApi } from './services/fabricApi';

// Premium Design Tokens & UI Primitives
import { C } from './components/dashboard/DashboardTokens';
import { injectStyles, Dot, Toast } from './components/dashboard/UIPrimitives';

// Modular Dashboard Components
import SmartBoard from './components/dashboard/SmartBoard';
import NetworkPanel from './components/dashboard/NetworkPanel';
import ChannelList from './components/dashboard/ChannelList';
import TransactionLedger from './components/dashboard/TransactionLedger';
import LogConsole from './components/dashboard/LogConsole';
import HealthMapper from './components/dashboard/HealthMapper';
import ReportGenerator from './components/dashboard/ReportGenerator';

/**
 * App.jsx — DiploChain V2 Unified Audit Dashboard
 * ─────────────────────────────────────────────────────────────────────
 * Orchestrator central pour le suivi de la blockchain, des microservices
 * et l'exécution de séquences d'audit automatisées.
 * ─────────────────────────────────────────────────────────────────────
 */
function App() {
  // Injection des styles globaux (Keyframes, Glassmorphism, etc.)
  injectStyles();

  // ─── États Globaux ──────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState("smart");
  const [toast, setToast] = useState(null);
  const [logMessages, setLogMessages] = useState([]);
  const [auditRunning, setAuditRunning] = useState(false);
  const [role, setRole] = useState('ADMIN');

  // ─── Hooks de Données (Polling Fabric V2) ───────────────────────────
  const { data: network, loading: netLoading, refresh: netRefresh } = useFabricNetwork();
  const { data: channels, loading: chLoading, refresh: chRefresh } = useFabricChannels();
  const { data: transactions, loading: txLoading } = useFabricTransactions();
  const { data: stats, refresh: statsRefresh } = useFabricStats();

  // ─── Helpers UI ─────────────────────────────────────────────────────
  const showToast = useCallback((message, type = "info") => setToast({ message, type }), []);
  
  const addLog = useCallback((msg, type = "info") => {
    setLogMessages(prev => [
      { t: new Date().toISOString(), msg, level: type.toUpperCase(), src: "audit-engine" }, 
      ...prev
    ].slice(0, 100)); // Garder les 100 derniers logs
  }, []);

  // ─── Séquence d'Audit Automatisée (Logique AppContent.jsx) ──────────
  const runFullAuditSequence = async () => {
    setAuditRunning(true);
    addLog(`Démarrage de l'Audit Complet (Rôle: ${role})...`, 'info');
    
    try {
      // 1. Authentification
      addLog("Step 1/4: Authentification Admin...", "info");
      const auth = await fabricApi.loginAdmin();
      if (auth.access_token) {
        localStorage.setItem("diplochain_token", auth.access_token);
        addLog("SUCCESS: JWT Token validé.", "success");
      }

      // 2. Test Microservice Institution
      addLog("Step 2/4: Vérification Institution Service...", "info");
      const inst = await fabricApi.createInstitution({ nom_institution: "Audit Academy", type: "UNIVERSITE" });
      addLog(`SUCCESS: Institution créée (ID: ${inst.institution_id})`, "success");

      // 3. Test Microservice Étudiant
      addLog("Step 3/4: Vérification Student Service...", "info");
      const stu = await fabricApi.createStudent({ nom: "AUDIT", prenom: "Core", email_etudiant: `audit_${Date.now()}@test.com` });
      addLog(`SUCCESS: Étudiant créé (ID: ${stu.etudiant_id})`, "success");

      // 4. Test Chaincode & Ledger
      addLog("Step 4/4: Test d'émission Ledger (RegisterDiploma)...", "info");
      await fabricApi.invokeChaincode({
        fn: "RegisterDiploma", 
        channel: "channel-1", 
        diplomeId: "AUDIT-" + Date.now().toString().slice(-4), 
        hash: "4A2D35A3E0C1F7...", 
        ipfsCid: "Qm-AUDIT-ROOT", 
        institutionId: "1", 
        etudiantId: "1", 
        date: new Date().toISOString().slice(0, 10)
      });
      addLog("SUCCESS: Transaction committée sur Fabric.", "success");

      showToast("Séquence d'Audit terminée avec succès", "success");
      statsRefresh(); // Rafraîchir les stats globales
    } catch (err) {
      addLog(`CRITICAL ERROR: ${err.message}`, "error");
      showToast("Échec de l'audit système", "error");
    } finally {
      setAuditRunning(false);
    }
  };

  // ─── Navigation & Router interne ────────────────────────────────────
  const TABS = [
    { id: "smart",        label: "Smart Board",    icon: "🚀" },
    { id: "network",      label: "Node Topology",  icon: "🖧" },
    { id: "channels",     label: "Ledger Channels",icon: "◈" },
    { id: "transactions", label: "Ledger Explorer", icon: "⚡" },
    { id: "health",       label: "System Health",  icon: "🗺" },
    { id: "logs",         label: "Real-time Logs", icon: "⬛" },
    { id: "reports",      label: "Audit Reports",  icon: "📄" },
  ];

  const renderActiveSection = () => {
    switch (activeTab) {
      case "smart":        return <SmartBoard stats={stats} onToast={showToast} addLog={addLog} onRunAudit={runFullAuditSequence} auditRunning={auditRunning} />;
      case "network":      return <NetworkPanel network={network} loading={netLoading} onRefresh={netRefresh} />;
      case "channels":     return <ChannelList channels={channels} loading={chLoading} onCreated={chRefresh} onToast={showToast} />;
      case "transactions": return <TransactionLedger transactions={transactions} loading={txLoading} onToast={showToast} />;
      case "health":       return <HealthMapper />;
      case "logs":         return <LogConsole initialLogs={logMessages} />;
      case "reports":      return <ReportGenerator stats={stats} onToast={showToast} />;
      default:             return <SmartBoard stats={stats} onToast={showToast} addLog={addLog} />;
    }
  };

  return (
    <Router>
      <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: C.sans, fontSize: 13, display: "flex", flexDirection: "column" }}>
        
        {/* Header Premium Unifié */}
        <header className="dc-glass" style={{ 
          position: "sticky", top: 0, zIndex: 100,
          padding: "14px 32px", display: "flex", alignItems: "center", justifyContent: "space-between",
          borderBottom: `1px solid ${C.border}`
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ 
              width: 40, height: 40, borderRadius: 10, background: C.blueG, 
              display: "flex", alignItems: "center", justifyContent: "center", 
              fontSize: 20, boxShadow: "0 0 20px rgba(59, 130, 246, 0.4)" 
            }}>⛓</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 17, letterSpacing: "-0.02em", color: "#fff" }}>DIPLOCHAIN <span style={{ color: C.blue }}>AUDIT</span></div>
              <div style={{ fontSize: 10, color: C.textMut, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em" }}>V2 Compliance Control Center</div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <div style={{ display: "flex", gap: 18, alignItems: "center", padding: "6px 20px", background: "rgba(0,0,0,0.3)", borderRadius: 30, border: `1px solid ${C.border}` }}>
               <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Dot status={network ? "active" : "down"} pulse />
                  <span style={{ fontSize: 10, fontWeight: 800, color: network ? C.green : C.red }}>{network ? "FABRIC LTS 2.5 ONLINE" : "NETWORK OFFLINE"}</span>
               </div>
               <div style={{ width: 1, height: 12, background: C.border }} />
               <select 
                 value={role} 
                 onChange={(e) => setRole(e.target.value)}
                 style={{ background: "transparent", border: "none", color: C.textSec, fontSize: 11, fontWeight: 700, outline: "none", cursor: "pointer" }}
               >
                 <option value="ADMIN">ROLE: SYSTEM ADMIN</option>
                 <option value="AUDITOR">ROLE: PROJECT AUDITOR</option>
               </select>
            </div>
            <div style={{ width: 34, height: 34, borderRadius: "50%", background: C.surfaceHi, border: `1px solid ${C.border}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>👤</div>
          </div>
        </header>

        <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
          
          {/* Menu de Navigation Sidebar */}
          <nav style={{ 
            width: 250, borderRight: `1px solid ${C.border}`, padding: "24px 12px", 
            display: "flex", flexDirection: "column", gap: 4, background: "rgba(10, 15, 29, 0.3)" 
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
                <span style={{ flex: 1 }}>{tab.label}</span>
                {activeTab === tab.id && <div style={{ width: 4, height: 4, borderRadius: "50%", background: C.blue }} />}
              </button>
            ))}
            
            <div style={{ marginTop: "auto", padding: "16px", borderRadius: 12, background: "rgba(18, 26, 46, 0.5)", border: `1px solid ${C.border}` }}>
               <div style={{ fontSize: 10, color: C.textMut, fontWeight: 800, textTransform: "uppercase", marginBottom: 12, letterSpacing: "0.05em" }}>Node Integrity</div>
               <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {["Orderer Service", "Peer0 Endorsement", "CouchDB Ledger"].map(n => (
                    <div key={n} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                       <span style={{ fontSize: 11, color: C.textSec, fontWeight: 500 }}>{n}</span>
                       <Dot status={network ? "active" : "down"} />
                    </div>
                  ))}
               </div>
            </div>
          </nav>

          {/* Section de Contenu Dynamique */}
          <main style={{ flex: 1, padding: "32px 48px", overflowY: "auto", background: `radial-gradient(circle at top right, ${C.surfaceHi}40, transparent)` }}>
            {renderActiveSection()}
          </main>

        </div>

        {/* Notifications Toast Système */}
        {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
      </div>
    </Router>
  );
}

export default App;