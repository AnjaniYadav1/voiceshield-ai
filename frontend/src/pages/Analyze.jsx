import React, { useEffect, useState } from "react";
import ModeBanner from "../components/ModeBanner.jsx";
import WaveformRecorder from "../components/WaveformRecorder.jsx";
import ResultPanel from "../components/ResultPanel.jsx";
import { analyzeFile, analyzeLive, listSpeakers } from "../services/api.js";

export default function Analyze() {
  const [speakers, setSpeakers] = useState([]);
  const [speakerId, setSpeakerId] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    listSpeakers().then(setSpeakers).catch(() => {});
  }, []);

  const runUploadAnalysis = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeFile(file, speakerId || undefined);
      setResult(data);
    } catch (e) {
      setError(e?.response?.data?.detail || "Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const runLiveAnalysis = async (blob) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeLive(blob, speakerId || undefined);
      setResult(data);
    } catch (e) {
      setError(e?.response?.data?.detail || "Live analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold">Live Voice Analysis</h1>
        <p className="text-inkdim text-sm mt-1">
          Upload a recording or capture audio live to check for voice-cloning
          indicators and verify against a registered speaker.
        </p>
      </div>

      <ModeBanner />

      <div className="grid lg:grid-cols-2 gap-6 mb-6">
        <div className="card p-5 space-y-4">
          <div className="text-sm text-inkdim">Upload audio file</div>
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-inkdim file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-panel2 file:text-ink file:text-sm hover:file:bg-line cursor-pointer"
          />

          <div>
            <label className="text-sm text-inkdim block mb-1.5">
              Compare against trusted speaker (optional)
            </label>
            <select
              value={speakerId}
              onChange={(e) => setSpeakerId(e.target.value)}
              className="w-full bg-panel2 border border-line rounded-lg px-3 py-2 text-sm"
            >
              <option value="">— No reference speaker —</option>
              {speakers.map((s) => (
                <option key={s.speaker_id} value={s.speaker_id}>
                  {s.name} ({s.speaker_id})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={runUploadAnalysis}
            disabled={!file || loading}
            className="px-4 py-2 rounded-lg bg-signal text-void font-semibold text-sm disabled:opacity-40 hover:opacity-90 transition"
          >
            {loading ? "Analyzing…" : "Analyze Uploaded File"}
          </button>
        </div>

        <WaveformRecorder onRecordingComplete={runLiveAnalysis} />
      </div>

      {error && (
        <div className="mb-6 px-4 py-3 rounded-lg border border-danger/40 bg-danger/10 text-danger text-sm">
          {error}
        </div>
      )}

      {loading && !result && (
        <div className="text-inkdim text-sm">Running analysis pipeline…</div>
      )}

      <ResultPanel result={result} />
    </div>
  );
}
