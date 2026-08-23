import React from "react";

/**
 * Renders a percentage as a row of waveform-style bars, echoing the sidebar
 * logo and tying every score display back to the "voice signal" motif.
 */
function colorFor(pct, kind) {
  if (kind === "safe-high") {
    // higher is better (e.g. speaker match)
    if (pct >= 70) return "#3DDC97";
    if (pct >= 45) return "#F5A623";
    return "#FF5470";
  }
  // default: higher is worse (ai probability, risk score)
  if (pct >= 65) return "#FF5470";
  if (pct >= 35) return "#F5A623";
  return "#3DDC97";
}

export default function RiskMeter({ label, value, kind = "danger-high" }) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
  const color = colorFor(pct, kind);
  const barCount = 24;
  const filled = Math.round((pct / 100) * barCount);

  return (
    <div>
      <div className="flex justify-between items-baseline mb-1.5">
        <span className="text-sm text-inkdim">{label}</span>
        <span className="mono-num text-lg font-semibold" style={{ color }}>
          {pct}%
        </span>
      </div>
      <div className="flex items-end gap-[2px] h-8">
        {Array.from({ length: barCount }).map((_, i) => {
          const isFilled = i < filled;
          const h = 30 + ((i % 5) * 8);
          return (
            <div
              key={i}
              className="flex-1 rounded-sm bar-anim"
              style={{
                height: `${h}%`,
                backgroundColor: isFilled ? color : "#233040",
                opacity: isFilled ? 1 : 0.6,
              }}
            />
          );
        })}
      </div>
    </div>
  );
}
