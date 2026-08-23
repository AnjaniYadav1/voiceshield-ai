import React, { useEffect, useState } from "react";
import { getHealth } from "../services/api.js";

export default function Settings() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {});
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold">System Information</h1>
        <p className="text-inkdim text-sm mt-1">
          VoiceShield AI — MVP / prototype build for Smart India Hackathon.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card p-5 space-y-3">
          <div className="text-sm text-inkdim">Backend Status</div>
          {health ? (
            <ul className="text-sm space-y-1.5">
              <li>Status: <span className="text-safe">{health.status}</span></li>
              <li>Operating mode: <span className="font-semibold">{health.mode.toUpperCase()}</span></li>
              <li>Prototype classifier trained: {health.detector_available ? "Yes" : "No (using heuristic / demo fallback)"}</li>
              <li>Speaker verification available: {health.speaker_verification_available ? "Yes" : "No"}</li>
            </ul>
          ) : (
            <div className="text-inkdim text-sm">Checking backend…</div>
          )}
        </div>

        <div className="card p-5 space-y-3 text-sm leading-relaxed text-inkdim">
          <div className="text-ink font-medium">Important disclaimers</div>
          <p>
            This is a hackathon MVP, not a certified or production-grade
            security product. Detection scores in <span className="text-ink">DEMO MODE</span>{" "}
            are fully simulated for demonstration purposes.
          </p>
          <p>
            In <span className="text-ink">REAL ML MODE</span>, authenticity
            scores come from a small prototype classifier trained on
            handcrafted acoustic features over a limited sample set — it is
            not a validated, state-of-the-art deepfake detector and should
            not be relied on for high-stakes decisions without further
            testing and larger training data.
          </p>
          <p>
            Speaker verification uses an MFCC-statistics voiceprint rather
            than a trained neural speaker-embedding model, due to offline
            development constraints. Only derived embeddings are stored for
            trusted speakers — never raw reference audio.
          </p>
        </div>
      </div>
    </div>
  );
}
