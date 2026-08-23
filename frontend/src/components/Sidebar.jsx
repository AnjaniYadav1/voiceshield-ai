import React from "react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/dashboard", label: "Overview", icon: "◈" },
  { to: "/analyze", label: "Live Analysis", icon: "▮▯" },
  { to: "/speakers", label: "Speaker Verification", icon: "◐" },
  { to: "/history", label: "Detection History", icon: "≣" },
  { to: "/analytics", label: "Threat Analytics", icon: "△" },
  { to: "/settings", label: "System Info", icon: "⚙" },
];

function LogoMark() {
  // Signature element: a small "waveform" mark built from bars, echoing
  // the risk meters used throughout the app.
  const heights = [6, 14, 20, 12, 18, 8];
  return (
    <div className="flex items-end gap-[3px] h-6">
      {heights.map((h, i) => (
        <div
          key={i}
          className="w-[3px] rounded-sm bg-signal"
          style={{ height: `${h}px`, opacity: 0.5 + (i % 3) * 0.15 }}
        />
      ))}
    </div>
  );
}

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-panel border-r border-line flex flex-col">
      <div className="px-6 py-6 border-b border-line">
        <div className="flex items-center gap-3">
          <LogoMark />
          <span className="font-display font-semibold text-lg tracking-tight">
            VoiceShield <span className="text-signal">AI</span>
          </span>
        </div>
        <p className="text-xs text-inkdim mt-2 leading-snug">
          Detect. Verify. Prevent Voice Impersonation.
        </p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-panel2 text-ink border border-line"
                  : "text-inkdim hover:text-ink hover:bg-panel2/60"
              }`
            }
          >
            <span className="w-5 text-center text-signal">{l.icon}</span>
            {l.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-6 py-4 border-t border-line text-[11px] text-inkdim leading-relaxed">
        MVP / Prototype build.
        <br />
        Not a certified security product.
      </div>
    </aside>
  );
}
