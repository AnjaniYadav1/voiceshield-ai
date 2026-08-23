import React from "react";
import RiskMeter from "./RiskMeter.jsx";

const classificationStyle = {
  REAL: { label: "REAL", color: "text-safe", border: "border-safe/40", bg: "bg-safe/10" },
  SUSPICIOUS: { label: "⚠️ SUSPICIOUS", color: "text-warn", border: "border-warn/40", bg: "bg-warn/10" },
  LIKELY_AI_GENERATED: { label: "⚠️ LIKELY AI-GENERATED", color: "text-danger", border: "border-danger/40", bg: "bg-danger/10" },
};

const severityDot = {
  ok: "bg-safe",
  warning: "bg-warn",
  critical: "bg-danger",
};

export default function ResultPanel({ result }) {
  if (!result) return null;
  const style = classificationStyle[result.classification] || classificationStyle.SUSPICIOUS;

  return (
    <div className="card p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <div className="text-xs uppercase tracking-wide text-inkdim">Classification</div>
          <div className={`text-2xl font-display font-semibold mt-1 ${style.color}`}>
            {style.label}
          </div>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold border ${style.border} ${style.bg} ${style.color}`}
        >
          RISK: {result.risk_level}
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <RiskMeter label="AI-Generated Probability" value={result.ai_probability} kind="danger-high" />
        {result.speaker_match !== null && result.speaker_match !== undefined ? (
          <RiskMeter label="Speaker Match" value={result.speaker_match} kind="safe-high" />
        ) : (
          <div className="text-sm text-inkdim flex items-center">
            No reference speaker supplied — identity not verified.
          </div>
        )}
        <RiskMeter label="Overall Risk" value={result.risk_score} kind="danger-high" />
      </div>

      <div>
        <div className="text-xs uppercase tracking-wide text-inkdim mb-2">Detected Signals</div>
        <ul className="space-y-1.5">
          {result.signals.map((s, i) => (
            <li key={i} className="flex items-center gap-2 text-sm">
              <span className={`w-1.5 h-1.5 rounded-full ${severityDot[s.severity] || "bg-inkdim"}`} />
              {s.label}
            </li>
          ))}
        </ul>
      </div>

      <div className="border-t border-line pt-4">
        <div className="text-xs uppercase tracking-wide text-inkdim mb-1">Recommendation</div>
        <p className="text-sm text-ink leading-relaxed">{result.recommendation}</p>
      </div>

      <div className="text-[11px] text-inkdim flex flex-wrap gap-x-4 gap-y-1 border-t border-line pt-3">
        <span>Model mode: <span className="text-inkdim/90 font-medium">{result.model_mode}</span></span>
        <span>Duration: {result.duration?.toFixed?.(2)}s</span>
        <span>File: {result.filename}</span>
      </div>
    </div>
  );
}
