/**
 * DashboardTokens.js
 * Premium design tokens for DiploChain V2
 */

export const C = {
  bg:        "#060912",
  surface:   "#0A0F1D",
  surfaceHi: "#121A2E",
  glass:     "rgba(10, 15, 29, 0.72)",
  border:    "rgba(30, 41, 67, 0.5)",
  borderHi:  "rgba(59, 130, 246, 0.3)",
  blue:      "#3B82F6",
  blueG:     "linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)",
  teal:      "#0EA5E9",
  tealG:     "linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%)",
  emerald:   "#10B981",
  green:     "#22C55E",
  amber:     "#F59E0B",
  red:       "#EF4444",
  violet:    "#8B5CF6",
  indigo:    "#6366F1",
  text:      "#F1F5F9",
  textSec:   "#94A3B8",
  textMut:   "#475569",
  mono:      "'JetBrains Mono', 'Fira Code', monospace",
  sans:      "'Inter', system-ui, -apple-system, sans-serif",
  shadow:    "0 8px 32px rgba(0, 0, 0, 0.4)",
  anim:      "cubic-bezier(0.4, 0, 0.2, 1)",
};

export const STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

  @keyframes dc-fadein  { from { opacity: 0; transform: translateY(10px); filter: blur(4px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }
  @keyframes dc-spin    { to { transform: rotate(360deg); } }
  @keyframes dc-pulse   { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
  @keyframes dc-shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
  @keyframes dc-blink   { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

  .dc-glass { 
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    background: ${C.glass};
    border: 1px solid ${C.border};
  }

  .dc-card {
    transition: all 0.25s ${C.anim};
    animation: dc-fadein 0.4s ${C.anim} both;
  }

  .dc-card:hover {
    border-color: ${C.borderHi};
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  }

  .dc-btn {
    transition: all 0.2s ${C.anim};
    transform-origin: center;
  }

  .dc-btn:active {
    transform: scale(0.96);
  }

  .dc-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .dc-row:hover {
    background: ${C.surfaceHi}cc !important;
  }

  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: ${C.border}; border-radius: 10px; }
  ::-webkit-scrollbar-thumb:hover { background: ${C.textMut}; }
`;
