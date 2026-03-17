import React from "react";
import DiplomasSection from "../sections/DiplomasSection";
import EnterpriseSection from "../sections/EnterpriseSection";
import BlockchainSection from "../sections/BlockchainSection";
import RetrySection from "../sections/RetrySection";
import AuditSection from "../sections/AuditSection";
import HealthSection from "../sections/HealthSection";

export default function MainDashboard() {
  const sections = [
    { key:'health', label:'Health', comp:<HealthSection/> },
    { key:'diplomas', label:'Diplomas', comp:<DiplomasSection/> },
    { key:'enterprise', label:'Enterprise', comp:<EnterpriseSection/> },
    { key:'blockchain', label:'Blockchain', comp:<BlockchainSection/> },
    { key:'retry', label:'Retry', comp:<RetrySection/> },
    { key:'audit', label:'Audit', comp:<AuditSection/> },
  ];
  const [active, setActive] = React.useState(sections[0].key);

  const activeSection = sections.find(s=>s.key===active);

  return (
    <div>
      <h1>Realtime Monitoring Dashboard</h1>
      <nav style={{ marginBottom:20 }}>
        {sections.map(s=>(
          <button
            key={s.key}
            onClick={()=>setActive(s.key)}
            style={{
              marginRight:6,
              padding:6,
              background: s.key===active ? '#ccc' : '#eee',
              border: '1px solid #999',
              borderRadius:4,
            }}
          >
            {s.label}
          </button>
        ))}
      </nav>
      {activeSection && activeSection.comp}
    </div>
  );
}
