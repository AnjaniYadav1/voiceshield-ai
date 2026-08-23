import React, { useEffect, useState } from "react";
import { listAnalyses, deleteAnalysis } from "../services/api.js";
import ResultPanel from "../components/ResultPanel.jsx";

const riskColor = { LOW: "text-safe", MEDIUM: "text-warn", HIGH: "text-danger" };

export default function History() {
  const [analyses, setAnalyses] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = () =>
    listAnalyses(100, 0)
      .then(setAnalyses)
      .catch(() => {})
      .finally(() => setLoading(false));

  useEffect(() => {
    refresh();
  }, []);

  const onDelete = async (id, e) => {
    e.stopPropagation();
    await deleteAnalysis(id);
    if (selected?.id === id) setSelected(null);
    refresh();
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold">Detection History</h1>
        <p className="text-inkdim text-sm mt-1">
          All previous analyses, most recent first. Select a row to view full
          explainability details.
        </p>
      </div>

      <div className="grid lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 card overflow-hidden">
          {loading ? (
            <div className="p-6 text-inkdim text-sm">Loading…</div>
          ) : analyses.length === 0 ? (
            <div className="p-6 text-inkdim text-sm">No analyses recorded yet.</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-panel2 text-inkdim text-xs uppercase">
                <tr>
                  <th className="text-left px-4 py-3">File</th>
                  <th className="text-left px-4 py-3">Classification</th>
                  <th className="text-left px-4 py-3">Risk</th>
                  <th className="text-left px-4 py-3">Time</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody>
                {analyses.map((a) => (
                  <tr
                    key={a.id}
                    onClick={() => setSelected(a)}
                    className={`border-t border-line cursor-pointer hover:bg-panel2/60 ${
                      selected?.id === a.id ? "bg-panel2/80" : ""
                    }`}
                  >
                    <td className="px-4 py-3 truncate max-w-[160px]">{a.filename}</td>
                    <td className="px-4 py-3">{a.classification.replace("_", " ")}</td>
                    <td className={`px-4 py-3 font-semibold ${riskColor[a.risk_level]}`}>
                      {a.risk_level}
                    </td>
                    <td className="px-4 py-3 text-inkdim">
                      {a.timestamp ? new Date(a.timestamp).toLocaleString() : "—"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={(e) => onDelete(a.id, e)}
                        className="text-inkdim hover:text-danger text-xs"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="lg:col-span-2">
          {selected ? (
            <ResultPanel result={selected} />
          ) : (
            <div className="card p-6 text-inkdim text-sm text-center">
              Select an analysis to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
