import React, { useEffect, useState } from "react";
import { listSpeakers, registerSpeaker } from "../services/api.js";

export default function Speakers() {
  const [speakers, setSpeakers] = useState([]);
  const [name, setName] = useState("");
  const [speakerId, setSpeakerId] = useState("");
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const refresh = () => listSpeakers().then(setSpeakers).catch(() => {});

  useEffect(() => {
    refresh();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    if (!name || !speakerId || !file) return;
    setLoading(true);
    setStatus(null);
    try {
      await registerSpeaker(name, speakerId, file);
      setStatus({ ok: true, msg: `Registered trusted speaker "${name}".` });
      setName("");
      setSpeakerId("");
      setFile(null);
      refresh();
    } catch (e2) {
      setStatus({ ok: false, msg: e2?.response?.data?.detail || "Registration failed." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold">Trusted Speaker Registration</h1>
        <p className="text-inkdim text-sm mt-1">
          Register a reference voice to enable speaker-match verification
          during analysis. Only the derived voiceprint (embedding) is stored
          — the reference audio itself is discarded after processing.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <form onSubmit={submit} className="card p-5 space-y-4">
          <div>
            <label className="text-sm text-inkdim block mb-1.5">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Priya Sharma"
              className="w-full bg-panel2 border border-line rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm text-inkdim block mb-1.5">Speaker ID</label>
            <input
              value={speakerId}
              onChange={(e) => setSpeakerId(e.target.value)}
              placeholder="e.g. priya_01"
              className="w-full bg-panel2 border border-line rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm text-inkdim block mb-1.5">Reference audio (clean, 5-15s of speech)</label>
            <input
              type="file"
              accept="audio/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-inkdim file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-panel2 file:text-ink file:text-sm hover:file:bg-line cursor-pointer"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !name || !speakerId || !file}
            className="px-4 py-2 rounded-lg bg-signal text-void font-semibold text-sm disabled:opacity-40 hover:opacity-90 transition"
          >
            {loading ? "Registering…" : "Register Trusted Speaker"}
          </button>
          {status && (
            <div className={`text-sm ${status.ok ? "text-safe" : "text-danger"}`}>{status.msg}</div>
          )}
        </form>

        <div className="card p-5">
          <div className="text-sm text-inkdim mb-4">Registered Trusted Speakers</div>
          {speakers.length === 0 ? (
            <div className="text-inkdim text-sm py-8 text-center">
              No trusted speakers registered yet.
            </div>
          ) : (
            <ul className="divide-y divide-line">
              {speakers.map((s) => (
                <li key={s.speaker_id} className="py-3 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">{s.name}</div>
                    <div className="text-xs text-inkdim">ID: {s.speaker_id}</div>
                  </div>
                  <div className="text-xs text-inkdim text-right">
                    <div>{s.embedding_method}</div>
                    <div>{new Date(s.created_at).toLocaleDateString()}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
