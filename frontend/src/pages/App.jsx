import { useEffect, useState } from "react";
import ProblemForm from "../components/ProblemForm";
import DiagnosisReport from "../components/DiagnosisReport";

const API_BASE = "http://localhost:8000/api";

export default function App() {
  const [diagnosis, setDiagnosis] = useState(null);
  const [dashboard, setDashboard] = useState(null);

  const refreshDashboard = async () => {
    try {
      const res = await fetch(`${API_BASE}/dashboard`);
      const data = res.ok ? await res.json() : null;
      if (data) setDashboard(data);
    } catch {
      setDashboard({ total_diagnoses: 0, verdict_breakdown: {} });
    }
  };

  useEffect(() => {
    refreshDashboard();
  }, []);

  return (
    <main className="app-shell">
      <h1 className="page-title">NetSage AI</h1>
      <p className="subtitle">Cisco troubleshooting assistant for VLAN, IP, routing, and ACL diagnosis.</p>

      {dashboard && (
        <section className="dashboard-strip panel" style={{ padding: 20, marginBottom: 20 }}>
          <h2 style={{ margin: "0 0 12px" }}>Human review dashboard</h2>
          <div className="dashboard-grid">
            <div className="stat-card">
              <span className="stat-label">Total diagnoses</span>
              <strong>{dashboard.total_diagnoses ?? 0}</strong>
            </div>
            <div className="stat-card">
              <span className="stat-label">Accepted</span>
              <strong>{dashboard.verdict_breakdown?.Correct ?? 0}</strong>
            </div>
            <div className="stat-card">
              <span className="stat-label">Edited</span>
              <strong>{dashboard.verdict_breakdown?.["Partially Correct"] ?? 0}</strong>
            </div>
            <div className="stat-card">
              <span className="stat-label">Rejected</span>
              <strong>{dashboard.verdict_breakdown?.Wrong ?? 0}</strong>
            </div>
          </div>
        </section>
      )}

      <div className="grid-two">
        <ProblemForm onDiagnosis={setDiagnosis} />
        <DiagnosisReport
          diagnosis={diagnosis}
          problemDescription={diagnosis?.issue ?? ""}
          onReviewSubmit={refreshDashboard}
        />
      </div>
    </main>
  );
}
