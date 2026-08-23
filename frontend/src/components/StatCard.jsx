import React from "react";

const accentMap = {
  signal: "text-signal",
  safe: "text-safe",
  warn: "text-warn",
  danger: "text-danger",
};

export default function StatCard({ label, value, accent = "signal", suffix = "" }) {
  return (
    <div className="card p-5">
      <div className="text-xs uppercase tracking-wide text-inkdim">{label}</div>
      <div className={`mono-num text-3xl font-semibold mt-2 ${accentMap[accent]}`}>
        {value}
        <span className="text-base text-inkdim ml-1">{suffix}</span>
      </div>
    </div>
  );
}
