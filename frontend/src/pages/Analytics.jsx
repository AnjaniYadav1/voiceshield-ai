import React, { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  ScatterChart, Scatter,
} from "recharts";
import { listAnalyses, getStatistics } from "../services/api.js";
import StatCard from "../components/StatCard.jsx";

export default function Analytics() {
  const [analyses, setAnalyses] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    Promise.all([listAnalyses(100, 0), getStatistics()])
      .then(([a, s]) => {
        setAnalyses(a);
        setStats(s);
      })
      .catch(() => {});
  }, []);

  const mismatchBuckets = { "0-25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0 };
  analyses.forEach((a) => {
    if (a.speaker_match === null || a.speaker_match === undefined) return;
    const mismatch = (1 - a.speaker_match) * 100;
    if (mismatch < 25) mismatchBuckets["0-25%"]++;
    else if (mismatch < 50) mismatchBuckets["25-50%"]++;
    else if (mismatch < 75) mismatchBuckets["50-75%"]++;
    else mismatchBuckets["75-100%"]++;
  });
  const mismatchData = Object.entries(mismatchBuckets).map(([bucket, count]) => ({ bucket, count }));

  const scatterData = analyses.map((a) => ({
    ai: Math.round(a.ai_probability * 100),
    risk: Math.round(a.risk_score * 100),
  }));

  const aiProbBuckets = { "0-20%": 0, "20-40%": 0, "40-60%": 0, "60-80%": 0, "80-100%": 0 };
  analyses.forEach((a) => {
    const p = a.ai_probability * 100;
    if (p < 20) aiProbBuckets["0-20%"]++;
    else if (p < 40) aiProbBuckets["20-40%"]++;
    else if (p < 60) aiProbBuckets["40-60%"]++;
    else if (p < 80) aiProbBuckets["60-80%"]++;
    else aiProbBuckets["80-100%"]++;
  });
  const aiProbData = Object.entries(aiProbBuckets).map(([bucket, count]) => ({ bucket, count }));

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold">Threat Analytics</h1>
        <p className="text-inkdim text-sm mt-1">
          Aggregate patterns across all recorded detection activity.
        </p>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Analyses" value={stats.total_analyses} accent="signal" />
          <StatCard label="High Risk Rate" value={stats.total_analyses ? Math.round((stats.high_risk_attempts / stats.total_analyses) * 100) : 0} suffix="%" accent="danger" />
          <StatCard label="Avg Risk Score" value={(stats.average_risk_score * 100).toFixed(0)} suffix="%" accent="warn" />
          <StatCard label="Mode" value={stats.mode.toUpperCase()} accent="signal" />
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <div className="text-sm text-inkdim mb-4">AI-Generated Probability Distribution</div>
          {aiProbData.every((d) => d.count === 0) ? (
            <div className="text-inkdim text-sm py-16 text-center">No data yet.</div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={aiProbData}>
                <CartesianGrid stroke="#233040" strokeDasharray="3 3" />
                <XAxis dataKey="bucket" stroke="#8CA0B3" fontSize={12} />
                <YAxis stroke="#8CA0B3" fontSize={12} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#121821", border: "1px solid #233040", fontSize: 12 }} />
                <Bar dataKey="count" fill="#4FD8E8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card p-5">
          <div className="text-sm text-inkdim mb-4">Speaker Mismatch Statistics</div>
          {mismatchData.every((d) => d.count === 0) ? (
            <div className="text-inkdim text-sm py-16 text-center">
              No speaker-verified analyses yet.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={mismatchData}>
                <CartesianGrid stroke="#233040" strokeDasharray="3 3" />
                <XAxis dataKey="bucket" stroke="#8CA0B3" fontSize={12} />
                <YAxis stroke="#8CA0B3" fontSize={12} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#121821", border: "1px solid #233040", fontSize: 12 }} />
                <Bar dataKey="count" fill="#FF5470" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card p-5 lg:col-span-2">
          <div className="text-sm text-inkdim mb-4">Risk Score vs. AI-Probability Correlation</div>
          {scatterData.length === 0 ? (
            <div className="text-inkdim text-sm py-16 text-center">No data yet.</div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <ScatterChart>
                <CartesianGrid stroke="#233040" strokeDasharray="3 3" />
                <XAxis dataKey="ai" name="AI Probability %" stroke="#8CA0B3" fontSize={12} domain={[0, 100]} />
                <YAxis dataKey="risk" name="Risk Score %" stroke="#8CA0B3" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: "#121821", border: "1px solid #233040", fontSize: 12 }} cursor={{ strokeDasharray: "3 3" }} />
                <Scatter data={scatterData} fill="#4FD8E8" />
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
