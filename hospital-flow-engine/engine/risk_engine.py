# engine/risk_engine.py

from collections import defaultdict, deque
from datetime import datetime


class RiskAgent:
    def __init__(self, window_size=3):
        """
        window_size: number of recent observations to reason over
        """
        self.window_size = window_size
        self.patient_history = defaultdict(lambda: deque(maxlen=window_size))
        self.patient_risk_state = {}

    # Observe
    def observe(self, patient_row: dict):
        """
        Observe a single patient timestep.
        """
        pid = patient_row["patient_id"]
        self.patient_history[pid].append(patient_row)

        # Initialize patient state if first seen
        if pid not in self.patient_risk_state:
            self.patient_risk_state[pid] = {
                "last_deterioration_time": None
            }

    # Trend Computation

    def _compute_trends(self, rows):
        """
        Computes slope-based trends across the window.
        """
        first = rows[0]
        last = rows[-1]

        trends = {
            "hr_slope": last["heart_rate"] - first["heart_rate"],
            "sbp_slope": last["sbp"] - first["sbp"],
            "troponin_slope": last.get("troponin", 0) - first.get("troponin", 0),
            "ck_mb_slope": last.get("ck_mb", 0) - first.get("ck_mb", 0),
        }

        return trends

    # Signal and trend scoring

    def _compute_signal(self, rows):
        """
        Disease-specific signal logic (heart attack).
        Includes static thresholds + trend-based reasoning.
        """
        score = 0
        reasons = []

        # -------- Static thresholds --------
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

            if r.get("ck_mb", 0) > 5:
                score += 1
                reasons.append("elevated_ck_mb")

        # -------- Trend analysis --------
        trends = self._compute_trends(rows)

        if trends["hr_slope"] > 10:
            score += 1
            reasons.append("worsening_heart_rate")

        if trends["sbp_slope"] < -15:
            score += 1
            reasons.append("falling_blood_pressure")

        if trends["troponin_slope"] > 0.02:  # rising cardiac biomarker
            score += 1
            reasons.append("rising_troponin_trend")

        if trends["ck_mb_slope"] > 1:
            score += 1
            reasons.append("rising_ck_mb_trend")
       
        return score, list(set(reasons)), trends

    # Update risk state

    def update(self, patient_id: str):
        """
        Update and return the patient's risk state.
        """
        history = self.patient_history[patient_id]

        if len(history) < self.window_size:
            return None  # not enough temporal data yet

        score, reasons, trends = self._compute_signal(history)

        now = history[-1]["timestamp"]
        state = self.patient_risk_state[patient_id]

        # -------- Worsening detection --------
        worsening = any(r in reasons for r in [
            "worsening_heart_rate",
            "falling_blood_pressure",
            "rising_troponin_trend",
            "rising_ck_mb_trend"
        ])

        # -------- Track deterioration time --------
        if worsening:
            state["last_deterioration_time"] = now
        else:
            last_bad = state.get("last_deterioration_time")
            if last_bad:
                stable_minutes = (now - last_bad).total_seconds() / 60

                if stable_minutes >= 60:
                    score -= 2
                    reasons.append("stable_for_60_min")
                elif stable_minutes >= 30:
                    score -= 1
                    reasons.append("stable_for_30_min")

        score = max(score, 0)

        # -------- Risk level mapping --------
        if score >= 6:
            level = "CRITICAL"
        elif score >= 4:
            level = "HIGH"
        elif score >= 2:
            level = "MODERATE"
        else:
            level = "LOW"

        # -------- Persist state --------
        self.patient_risk_state[patient_id].update({
            "risk_level": level,
            "signal_score": score,
            "confidence": min(len(history) / self.window_size, 1.0),
            "reasons": reasons,
            "trends": trends
        })

        return self.patient_risk_state[patient_id]
