import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = "/api";

export default function DoctorDashboard() {
  const navigate = useNavigate();
  const [outputs, setOutputs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function fetchSimulation() {
      try {
        const res = await fetch(`${API_BASE}/simulation/run`);
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          setError(data.detail || "Failed to load simulation.");
          return;
        }
        if (!cancelled) setOutputs(data.outputs || []);
      } catch (e) {
        if (!cancelled) setError("Cannot reach backend. Is it running on port 8000?");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchSimulation();
    return () => { cancelled = true; };
  }, []);

  const handlePatientClick = async (record) => {
    setSelectedRecord(record);
    setSummary("");
    setSummaryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/reasoning/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          simulation_record: record,
          audience: "doctor",
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) setSummary(data.explanation || "");
      else setSummary(data.detail || "Failed to get explanation.");
    } catch (e) {
      setSummary("Could not reach LLM. Is the backend (and Ollama) running?");
    } finally {
      setSummaryLoading(false);
    }
  };

  const closeModal = () => {
    setSelectedRecord(null);
    setSummary("");
  };

  // Stats from backend
  const totalPatients = outputs.length;
  const byRisk = outputs.reduce((acc, o) => {
    const r = o.risk_level || "unknown";
    acc[r] = (acc[r] || 0) + 1;
    return acc;
  }, {});
  const byDecision = outputs.reduce((acc, o) => {
    const d = o.decision || "unknown";
    acc[d] = (acc[d] || 0) + 1;
    return acc;
  }, {});
  const avgPressure = totalPatients
    ? outputs.reduce((s, o) => s + (Number(o.pressure) || 0), 0) / totalPatients
    : 0;

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.title}>Doctor Dashboard</h1>
        <p style={styles.subtitle}>Heart attack patient monitoring · Agentic AI</p>
        <button style={styles.logout} onClick={() => navigate("/")}>
          Logout
        </button>
      </header>

      {loading ? (
        <p style={styles.center}>Loading simulation from backend…</p>
      ) : error ? (
        <p style={styles.error}>{error}</p>
      ) : (
        <>
          <section style={styles.stats}>
            <h2 style={styles.sectionTitle}>Stats (from hospital flow engine)</h2>
            <div style={styles.statGrid}>
              <div style={styles.statCard}>
                <div style={styles.statValue}>{totalPatients}</div>
                <div style={styles.statLabel}>Total patients</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statValue}>{avgPressure.toFixed(2)}</div>
                <div style={styles.statLabel}>Avg pressure</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statValue}>Risk</div>
                <div style={styles.statLabel}>
                  {Object.entries(byRisk).map(([k, v]) => `${k}: ${v}`).join(" · ")}
                </div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statValue}>Decision</div>
                <div style={styles.statLabel}>
                  {Object.entries(byDecision).map(([k, v]) => `${k}: ${v}`).join(" · ")}
                </div>
              </div>
            </div>
          </section>

          <section style={styles.patients}>
            <h2 style={styles.sectionTitle}>Patients — click for LLM summary</h2>
            <div style={styles.patientList}>
              {outputs.map((o) => (
                <button
                  key={o.patient_id}
                  style={styles.patientChip}
                  onClick={() => handlePatientClick(o)}
                >
                  {o.patient_id}
                  <span style={styles.chipMeta}>
                    {o.risk_level} · {o.decision}
                  </span>
                </button>
              ))}
            </div>
          </section>
        </>
      )}

      {selectedRecord && (
        <div style={styles.modalOverlay} onClick={closeModal}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>Patient summary — {selectedRecord.patient_id}</h3>
              <button style={styles.closeBtn} onClick={closeModal}>×</button>
            </div>
            <div style={styles.modalBody}>
              {summaryLoading ? (
                <p>Asking LLM for summary…</p>
              ) : (
                <div style={styles.summaryText}>{summary || "—"}</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  page: { minHeight: "100vh", background: "#f0f4f8", padding: "24px" },
  header: { marginBottom: "24px", position: "relative" },
  title: { margin: 0, fontSize: "28px", color: "#0f766e" },
  subtitle: { margin: "4px 0 0", fontSize: "14px", color: "#64748b" },
  logout: {
    position: "absolute",
    top: 0,
    right: 0,
    padding: "8px 16px",
    background: "#0f766e",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
  center: { textAlign: "center", padding: "48px", color: "#64748b" },
  error: { color: "#dc2626", padding: "24px", textAlign: "center" },
  stats: { marginBottom: "32px" },
  sectionTitle: { fontSize: "18px", marginBottom: "12px", color: "#334155" },
  statGrid: { display: "flex", flexWrap: "wrap", gap: "16px" },
  statCard: {
    minWidth: "140px",
    padding: "16px",
    background: "#fff",
    borderRadius: "12px",
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
  },
  statValue: { fontSize: "20px", fontWeight: "700", color: "#0f766e" },
  statLabel: { fontSize: "12px", color: "#64748b", marginTop: "4px" },
  patients: {},
  patientList: { display: "flex", flexWrap: "wrap", gap: "10px" },
  patientChip: {
    padding: "10px 16px",
    background: "#fff",
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "14px",
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
  },
  chipMeta: { fontSize: "11px", color: "#64748b", marginTop: "4px" },
  modalOverlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  modal: {
    background: "#fff",
    borderRadius: "16px",
    maxWidth: "520px",
    width: "90%",
    maxHeight: "80vh",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
    boxShadow: "0 20px 40px rgba(0,0,0,0.2)",
  },
  modalHeader: {
    padding: "16px 20px",
    borderBottom: "1px solid #e2e8f0",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  closeBtn: {
    background: "none",
    border: "none",
    fontSize: "24px",
    cursor: "pointer",
    color: "#64748b",
  },
  modalBody: { padding: "20px", overflowY: "auto", flex: 1 },
  summaryText: { whiteSpace: "pre-wrap", lineHeight: 1.6, color: "#334155" },
};
