import { useState } from "react";
import { useNavigate } from "react-router-dom";

/* ---------- Animation CSS ---------- */
const animationStyles = `
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
`;

export default function Login() {
  const [mode, setMode] = useState("login");
  const [role, setRole] = useState("doctor");
  const navigate = useNavigate();

  const handleLogin = () => {
    if (role === "doctor") navigate("/doctor");
    else if (role === "ops") navigate("/ops");
    else if (role === "admin") navigate("/admin");
    else navigate("/");
  };

  return (
    <>
      <style>{animationStyles}</style>

      <div style={styles.page}>
        <div style={styles.background} />

        <div style={styles.card}>
          <h1 style={styles.title}>JIVY</h1>
          <p style={styles.tagline}>
            When patient care can't wait, JIVY doesn't either.
          </p>

          {mode === "login" ? (
            <>
              <select
                style={styles.input}
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="doctor">Doctor</option>
                <option value="ops">Operations Manager</option>
                <option value="admin">Hospital Admin</option>
              </select>

              <button style={styles.button} onClick={handleLogin}>
                Login
              </button>

              <p style={styles.link} onClick={() => setMode("request")}>
                New user? Request access
              </p>
            </>
          ) : (
            <>
              <input style={styles.input} placeholder="Full Name" />
              <input style={styles.input} placeholder="Work Email" />

              <select style={styles.input}>
                <option>Doctor</option>
                <option>Operations Manager</option>
                <option>Hospital Admin</option>
              </select>

              <select style={styles.input}>
                <option>CityCare Hospital</option>
                <option>Apollo Hospital</option>
                <option>Fortis Healthcare</option>
              </select>

              <button style={styles.button}>Submit Request</button>

              <p style={styles.link} onClick={() => setMode("login")}>
                Back to Login
              </p>
            </>
          )}
        </div>
      </div>
    </>
  );
}

/* ---------- Styles ---------- */
const styles = {
  page: {
    width: "100vw",
    height: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
    overflow: "hidden",
  },

  background: {
    position: "absolute",
    inset: 0,
    backgroundImage: `
      linear-gradient(
        135deg,
        rgba(15,118,110,0.75),
        rgba(37,99,235,0.75),
        rgba(109,40,217,0.75)
      ),
      url("/ecg-bg.jpg")
    `,
    backgroundSize: "cover",
    backgroundPosition: "center",
    filter: "blur(22px)",
    transform: "scale(1.05)",
    zIndex: 0,
  },

  card: {
    width: "420px",
    maxWidth: "90%",
    padding: "32px",
    borderRadius: "18px",
    background: "rgba(255, 255, 255, 0.18)",
    backdropFilter: "blur(14px)",
    color: "#ffffff",
    boxShadow: "0 20px 40px rgba(0,0,0,0.35)",
    zIndex: 1,
    animation: "fadeInUp 0.6s ease-out",
  },

  title: {
    textAlign: "center",
    fontSize: "34px",
    fontWeight: "700",
    marginBottom: "8px",
  },

  tagline: {
    textAlign: "center",
    fontSize: "14px",
    marginBottom: "24px",
    opacity: 0.9,
  },

  input: {
    width: "100%",
    padding: "12px",
    marginBottom: "14px",
    borderRadius: "8px",
    border: "none",
    outline: "none",
  },

  button: {
    width: "100%",
    padding: "12px",
    borderRadius: "8px",
    border: "none",
    backgroundColor: "#14b8a6",
    color: "#ffffff",
    fontWeight: "600",
    cursor: "pointer",
  },

  link: {
    marginTop: "16px",
    textAlign: "center",
    fontSize: "14px",
    cursor: "pointer",
    textDecoration: "underline",
    opacity: 0.9,
  },
};
