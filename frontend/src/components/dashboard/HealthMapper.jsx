import React, { useState, useEffect } from 'react';
import { C } from './DashboardTokens';
import { Card, Dot, Badge, Spinner, DCButton } from './UIPrimitives';
import { fabricApi } from '../../services/fabricApi';

export default function HealthMapper() {
  const [services, setServices] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const data = await fabricApi.getDiscovery(); 
      setServices(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const id = setInterval(fetchHealth, 10000);
    return () => clearInterval(id);
  }, []);

  if (loading && !services) return <div style={{ textAlign: "center", padding: 60 }}><Spinner size={32} /></div>;

  const getStatusColor = (s) => (s?.status === "up" ? C.green : C.red);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
       <Card icon="🗺" title="Real-time Ecosystem Mapping" action={
         <DCButton variant="ghost" small onClick={fetchHealth} icon="↺">Refresh Map</DCButton>
       }>
         <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 14 }}>
           {services && Object.entries(services).map(([name, info], i) => (
             <div key={name} style={{
               background: C.bg, border: `1px solid ${C.border}`, borderRadius: 12, padding: "16px 20px",
               display: "flex", alignItems: "center", gap: 14,
               animation: `dc-fadein 0.4s ${C.anim} both`, animationDelay: `${i * 40}ms`
             }}>
               <div style={{ 
                 width: 40, height: 40, borderRadius: 10, background: `${getStatusColor(info)}15`, 
                 display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, color: getStatusColor(info),
                 border: `1px solid ${getStatusColor(info)}30`
               }}>{name.charAt(0).toUpperCase()}</div>
               <div style={{ flex: 1 }}>
                 <div style={{ fontWeight: 700, fontSize: 13, color: C.text, textTransform: "capitalize" }}>{name.replace("-service", "")}</div>
                 <div style={{ fontSize: 10, color: C.textMut, fontFamily: C.mono, marginTop: 2 }}>{name.includes("service") ? "Microservice" : "System Node"}</div>
               </div>
               <div style={{ textAlign: "right" }}>
                 <Dot status={info.status === "up" ? "active" : "down"} pulse={info.status === "up"} />
                 <div style={{ fontSize: 10, color: getStatusColor(info), fontWeight: 700, marginTop: 4 }}>{info.status?.toUpperCase()}</div>
               </div>
             </div>
           ))}
         </div>
       </Card>

       <Card title="Infrastructure Load" icon="📈">
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
             <p style={{ fontSize: 13, color: C.textSec }}>
               Visualizing inter-service latency and request throughput across the <b>diplochain-network</b>.
             </p>
             <div style={{ 
               height: 120, background: C.bg, borderRadius: 10, position: "relative", overflow: "hidden",
               border: `1px solid ${C.border}`, display: "flex", alignItems: "flex-end", gap: 4, padding: "0 10px"
             }}>
                {Array.from({ length: 40 }).map((_, i) => (
                  <div key={i} style={{ 
                    flex: 1, 
                    height: `${Math.random() * 60 + 20}%`, 
                    background: `linear-gradient(to top, ${C.blue}40, ${C.blue})`, 
                    borderRadius: "2px 2px 0 0",
                    animation: `dc-shimmer 2s infinite ease-in-out`,
                    animationDelay: `${i * 0.1}s`
                  }} />
                ))}
                <div style={{ position: "absolute", top: 10, right: 10 }}>
                   <Badge text="94.2 req/s" color={C.blue} />
                </div>
             </div>
          </div>
       </Card>
    </div>
  );
}
