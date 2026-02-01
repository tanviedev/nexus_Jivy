# engine/risk_engine.py

from collections import defaultdict, deque


class RiskAgent:
    """
    Patient Risk & Clinical State Agent
    ----------------------------------
    - Maintains rolling patient history
    - Computes static + trend-based risk signals
    - Applies time-aware stabilization decay
    - Outputs explainable risk states
    """

    def __init__(self, window_size=3):
        self.window_size = window_size
        self.patient_history = defaultdict(lambda: deque(maxlen=window_size))
        self.patient_risk_state = {}

    # --------------------------------------------------
    # 1️⃣ OBSERVE PATIENT STATE
    # --------------------------------------------------
    def observe(self, patient_row: dict):
        """
        Observe a single patient timestep.
        """
        pid = patient_row["patient_id"]
        self.patient_history[pid].append(patient_row)

        # Initialize patient state on first observation
        if pid not in self.patient_risk_state:
            self.patient_risk_state[pid] = {
                "last_deterioration_time": None
            }

    # --------------------------------------------------
    # 2️⃣ TREND COMPUTATION (SLOPES)
    # --------------------------------------------------
    def _compute_trends(self, rows):
        """
        Computes slope-based trends across the window.
        """
        first = rows[0]
        last = rows[-1]

        return {
            "hr_slope": last["heart_rate"] - first["heart_rate"],
            "sbp_slope": last["sbp"] - first["sbp"],
            "troponin_slope": last.get("troponin", 0) - first.get("troponin", 0),
            "ck_mb_slope": last.get("ck_mb", 0) - first.get("ck_mb", 0),
        }

    # --------------------------------------------------
    # 3️⃣ SIGNAL COMPUTATION (STATIC + TRENDS)
    # --------------------------------------------------
    def _compute_signal(self, rows):
        """
        Disease-specific logic: HEART ATTACK
        Combines static thresholds and trend-based reasoning.
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

            if r.get("troponin", 0) > 0.04:
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

        if trends["troponin_slope"] > 0.02:
            score += 1
            reasons.append("rising_troponin_trend")

        if trends["ck_mb_slope"] > 1:
            score += 1
            reasons.append("rising_ck_mb_trend")

        return score, list(set(reasons)), trends

    # --------------------------------------------------
    # 4️⃣ UPDATE RISK STATE (TIME-AWARE)
    # --------------------------------------------------
    def update(self, patient_id: str):
        """
        Update and return the patient's risk state.
        """
        history = self.patient_history[patient_id]

        if len(history) < self.window_size:
            return None  # insufficient temporal context

        score, reasons, trends = self._compute_signal(history)

        now = history[-1]["timestamp"]
        state = self.patient_risk_state[patient_id]

        # -------- Detect deterioration --------
        worsening = any(r in reasons for r in [
            "worsening_heart_rate",
            "falling_blood_pressure",
            "rising_troponin_trend",
            "rising_ck_mb_trend"
        ])

        # -------- Time-based stabilization decay --------
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
        state.update({
            "risk_level": level,
            "signal_score": score,
            "confidence": min(len(history) / self.window_size, 1.0),
            "reasons": reasons,
            "trends": trends
        })

        return state
