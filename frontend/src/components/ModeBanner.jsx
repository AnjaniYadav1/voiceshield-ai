import React, { useEffect, useState } from "react";
import { getHealth } from "../services/api.js";

export default function ModeBanner() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setError(true));
  }, []);

  if (error) {
    return (
      <div className="mb-6 px-4 py-2.5 rounded-lg border border-danger/40 bg-danger/10 text-danger text-sm">
        Cannot reach the VoiceShield backend at the configured API URL. Is
        <code className="mx-1 px-1.5 py-0.5 rounded bg-panel2">uvicorn</code>
        running on port 8000?
      </div>
    );
  }
  if (!health) return null;

  const isDemo = health.mode === "demo";

  return (
    <div
      className={`mb-6 px-4 py-2.5 rounded-lg border text-sm flex items-center gap-2 ${
        isDemo
          ? "border-warn/40 bg-warn/10 text-warn"
          : "border-safe/40 bg-safe/10 text-safe"
      }`}
    >
      <span className="font-semibold">
        {isDemo ? "DEMO MODE" : "REAL ML MODE"}
      </span>
      <span className="text-inkdim">
        {isDemo
          ? "— results are simulated for demonstration, not real model predictions."
          : "— running the prototype feature-based detection pipeline."}
      </span>
    </div>
  );
}
