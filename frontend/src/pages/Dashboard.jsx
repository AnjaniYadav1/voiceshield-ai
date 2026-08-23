import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import StatCard from "../components/StatCard.jsx";
import ModeBanner from "../components/ModeBanner.jsx";
import { getStatistics, listAnalyses } from "../services/api.js";

const RISK_COLORS = { LOW: "#3DDC97", MEDIUM: "#F5A623", HIGH: "#FF5470" };

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getStatistics(), listAnalyses(30, 0)])
      .then(([statsData, analyses]) => {
        setStats(statsData);
        const ordered = [...analyses].reverse();
        setTimeline(
          ordered.map((a, i) => ({
            index: i + 1,
            risk: Math.round(a.risk_score * 100),
            ai: Math.round(a.ai_probability * 100),
          }))
        );
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const pieData = stats
    ? [
        { name: "Low", value: stats.risk_distribution.LOW || 0, color: RISK_COLORS.LOW },
        { name: "Medium", value: stats.risk_distribution.MEDIUM || 0, color: RISK_COLORS.MEDIUM },
        { name: "High", value: stats.risk_distribution.HIGH || 0, color: RISK_COLORS.HIGH },
      ]
    : [];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-display font-semibold">Security Overview</h1>
        <p className="text-inkdim text-sm mt-1">
          Real-time posture across all voice-impersonation detection activity.
        </p>
      </div>

      <ModeBanner />

      {loading ? (
        <div className="text-inkdim text-sm">Loading dashboard…</div>
      ) : !stats ? (
        <div className="text-inkdim text-sm">No data available yet.</div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <StatCard label="Total Analyses" value={stats.total_analyses} accent="signal" />
            <StatCard label="Safe Voices" value={stats.safe_voices} accent="safe" />
            <StatCard label="Suspicious Voices" value={stats.suspicious_voices} accent="warn" />
            <StatCard label="High Risk Attempts" value={stats.high_risk_attempts} accent="danger" />
            <StatCard
              label="Avg Risk Score"
              value={(stats.average_risk_score * 100).toFixed(0)}
              suffix="%"
              accent="signal"
            />
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <div className="card p-5 lg:col-span-2">
              <div className="text-sm text-inkdim mb-4">
                Detection Timeline (risk score &amp; AI-probability, most recent analyses)
              </div>
              {timeline.length === 0 ? (
                <div className="text-inkdim text-sm py-12 text-center">
                  No analyses yet — run one from{" "}
                  <a href="/analyze" className="text-signal underline">
                    Live Analysis
                  </a>
                  .
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={timeline}>
                    <CartesianGrid stroke="#233040" strokeDasharray="3 3" />
                    <XAxis dataKey="index" stroke="#8CA0B3" fontSize={12} />
                    <YAxis stroke="#8CA0B3" fontSize={12} domain={[0, 100]} />
                    <Tooltip
                      contentStyle={{ background: "#121821", border: "1px solid #233040", fontSize: 12 }}
                    />
                    <Line type="monotone" dataKey="risk" stroke="#FF5470" strokeWidth={2} dot={false} name="Risk %" />
                    <Line type="monotone" dataKey="ai" stroke="#4FD8E8" strokeWidth={2} dot={false} name="AI Prob %" />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="card p-5">
              <div className="text-sm text-inkdim mb-4">Risk Distribution</div>
              {stats.total_analyses === 0 ? (
                <div className="text-inkdim text-sm py-12 text-center">No analyses yet.</div>
              ) : (
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={3}>
                      {pieData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ background: "#121821", border: "1px solid #233040", fontSize: 12 }} />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
