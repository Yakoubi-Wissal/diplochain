import React, { useEffect } from 'react';
import { C, STYLES } from './DashboardTokens';

export const injectStyles = (() => {
  let injected = false;
  return () => {
    if (injected) return;
    const el = document.createElement("style");
    el.textContent = STYLES;
    document.head.appendChild(el);
    injected = true;
  };
})();

export function Dot({ status = "active", pulse = false }) {
  const map = { 
    running: C.green, active: C.green, VALID: C.green, up: C.green,
    PENDING: C.amber, warning: C.amber, 
    ERROR: C.red, stopped: C.red, down: C.red 
  };
  const color = map[status] || C.textMut;
  return (
    <span style={{
      display: "inline-block", width: 8, height: 8, borderRadius: "50%",
      background: color, boxShadow: `0 0 8px ${color}80`,
      animation: (pulse || status === "PENDING") ? "dc-pulse 1.4s infinite" : "none",
      flexShrink: 0,
    }} />
  );
}

export function Badge({ text, color = C.blue, outline = false }) {
  return (
    <span style={{
      padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 700,
      fontFamily: C.mono, background: outline ? "transparent" : `${color}15`, 
      color, border: `1px solid ${color}40`, letterSpacing: ".02em", whiteSpace: "nowrap",
      textTransform: "uppercase"
    }}>{text}</span>
  );
}

export function Spinner({ size = 16, color = C.text }) {
  return (
    <span style={{
      display: "inline-block", width: size, height: size,
      border: `2px solid ${color}30`, borderTopColor: color,
      borderRadius: "50%", animation: "dc-spin .7s linear infinite",
    }} />
  );
}

export function DCButton({ children, onClick, variant = "primary", small, loading, disabled, icon, fullWidth }) {
  const styles = {
    primary: { bg: C.blueG,   color: "#fff",       border: "transparent" },
    teal:    { bg: C.tealG,   color: "#fff",       border: "transparent" },
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
        display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 8,
        padding: small ? "6px 14px" : "10px 20px",
        background: s.bg, color: s.color,
        border: `1px solid ${s.border}`,
        borderRadius: 8, cursor: disabled ? "not-allowed" : "pointer",
        fontSize: small ? 12 : 13, fontWeight: 600, fontFamily: C.sans,
        width: fullWidth ? "100%" : "auto",
        boxShadow: variant === "primary" ? "0 4px 12px rgba(59, 130, 246, 0.3)" : "none",
      }}
    >
      {loading ? <Spinner size={14} color={s.color} /> : icon}
      {children}
    </button>
  );
}

export function Card({ children, style = {}, delay = 0, noPadding, title, icon, action }) {
  return (
    <div className="dc-card dc-glass" style={{
      borderRadius: 12, padding: noPadding ? 0 : "20px 24px",
      animationDelay: `${delay}ms`, ...style,
    }}>
      {(title || icon || action) && (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: noPadding ? 0 : 20, padding: noPadding ? "20px 24px" : 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {icon && <div style={{ fontSize: 18, color: C.blue }}>{icon}</div>}
            <div style={{ fontWeight: 700, fontSize: 15, color: C.text, letterSpacing: "-0.01em" }}>{title}</div>
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}

export function StatCard({ label, value, sub, color = C.blue, icon, delay = 0, trend }) {
  return (
    <Card delay={delay} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <span style={{ fontSize: 11, color: C.textMut, textTransform: "uppercase", letterSpacing: ".1em", fontWeight: 700 }}>{label}</span>
        <div style={{ 
          width: 36, height: 36, borderRadius: 10, background: `${color}15`, 
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, color: color,
          border: `1px solid ${color}30`
        }}>{icon}</div>
      </div>
      <div style={{ fontSize: 32, fontWeight: 700, color: C.text, fontFamily: C.mono, letterSpacing: "-0.03em" }}>{value}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {trend && <span style={{ fontSize: 12, color: trend > 0 ? C.green : C.red, fontWeight: 600 }}>{trend > 0 ? "+" : ""}{trend}%</span>}
        <span style={{ fontSize: 12, color: C.textSec }}>{sub}</span>
      </div>
    </Card>
  );
}

export function Toast({ message, type = "info", onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const map = { success: C.green, error: C.red, info: C.blue, warning: C.amber };
  const color = map[type] || C.blue;

  return (
    <div style={{
      position: "fixed", bottom: 24, right: 24, zIndex: 2000,
      background: C.surface, border: `1px solid ${color}40`, borderRadius: 12,
      padding: "12px 20px", boxShadow: C.shadow, display: "flex", alignItems: "center", gap: 12,
      animation: "dc-slide-up 0.3s ease-out forwards", color: C.text, fontSize: 13, fontWeight: 600,
      minWidth: 280, backdropFilter: "blur(10px)"
    }}>
      <Dot status={type.toUpperCase() === "INFO" ? "active" : type.toUpperCase()} pulse />
      <div style={{ flex: 1 }}>{message}</div>
      <button onClick={onClose} style={{ 
        background: "transparent", border: "none", color: C.textMut, cursor: "pointer", fontSize: 18,
        display: "flex", alignItems: "center", justifyContent: "center", padding: 4
      }}>×</button>
    </div>
  );
}
