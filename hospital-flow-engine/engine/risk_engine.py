# engine/risk_engine.py

from collections import defaultdict, deque

class RiskAgent:
    def __init__(self, window_size=3):
        """
        window_size: number of recent observations to reason over
        """
        self.window_size = window_size
        self.patient_history = defaultdict(lambda: deque(maxlen=window_size))
        self.patient_risk_state = {}

    def observe(self, patient_row: dict):
        """
        Observe a single patient timestep.
        """
        pid = patient_row["patient_id"]
        self.patient_history[pid].append(patient_row)

    def _compute_signal(self, rows):
        """
        Disease-specific signal logic (heart attack).
        Stateless logic used internally.
        """
        score = 0
        reasons = []

        for r in rows:
            if r["heart_rate"] > 100:
                score += 1
                reasons.append("tachycardia")

            if r["sbp"] < 100:
                score += 1
                reasons.append("hypotension")

            if r["troponin"] > 0.04:
                score += 2
                reasons.append("elevated_troponin")

            if r["ck_mb"] > 5:
                score += 1
                reasons.append("elevated_ck_mb")

        return score, list(set(reasons))

    def update(self, patient_id: str):
        """
        Update and return the patient's risk state.
        """
        history = self.patient_history[patient_id]

        if len(history) < self.window_size:
            return None  # not enough data yet

        score, reasons = self._compute_signal(history)

        if score >= 5:
            level = "CRITICAL"
        elif score >= 3:
            level = "HIGH"
        elif score >= 1:
            level = "MODERATE"
        else:
            level = "LOW"

        self.patient_risk_state[patient_id] = {
            "risk_level": level,
            "signal_score": score,
            "confidence": min(len(history) / self.window_size, 1.0),
            "reasons": reasons
        }

        return self.patient_risk_state[patient_id]
