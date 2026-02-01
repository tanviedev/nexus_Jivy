# engine/decision_engine.py

def decide(risk_state, resource_state):
    """
    Decide hospital action based on patient risk state
    and current hospital resource constraints.
    """

    pressure = resource_state["pressure"]
    icu_full = resource_state.get("icu_full", False)

    risk_level = risk_state["risk_level"]
    confidence = risk_state.get("confidence", 1.0)
    reasons = risk_state.get("reasons", [])

    # -------- Detect worsening trends --------
    worsening_indicators = [
        "worsening_heart_rate",
        "falling_blood_pressure",
        "rising_troponin_trend",
        "rising_ck_mb_trend"
    ]

    worsening = any(r in reasons for r in worsening_indicators)

    # --------------------------------------------------
    # 1️⃣ HARD CAPACITY CONSTRAINT (GLOBAL OVERRIDE)
    # --------------------------------------------------
    if pressure >= 0.9:
        return "BLOCK", "Hospital at critical capacity"

    # --------------------------------------------------
    # 2️⃣ CRITICAL RISK
    # --------------------------------------------------
    if risk_level == "CRITICAL":
        if icu_full:
            return "ESCALATE", "Critical risk but ICU unavailable"
        return "PRIORITIZE", "Critical patient prioritized"

    # --------------------------------------------------
    # 3️⃣ HIGH RISK
    # --------------------------------------------------
    if risk_level == "HIGH":
        if worsening and confidence >= 0.8:
            return "PRIORITIZE", "High risk with worsening trends"

        if pressure >= 0.75:
            return "DELAY", "High risk but system overloaded"

        return "ALLOW", "High risk, resources available"

    # --------------------------------------------------
    # 4️⃣ MODERATE RISK
    # --------------------------------------------------
    if risk_level == "MODERATE":
        if worsening:
            return "OBSERVE", "Moderate risk with early deterioration"
        return "ALLOW", "Moderate risk stable"

    # --------------------------------------------------
    # 5️⃣ LOW RISK
    # --------------------------------------------------
    return "OBSERVE", "Risk stable"
