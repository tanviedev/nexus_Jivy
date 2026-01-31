# engine/decision_engine.py

def decide(risk_state, resource_state):
    """
    Decide hospital action based on patient risk and hospital resource state.
    """
    pressure = resource_state["pressure"]
    risk_level = risk_state["risk_level"]
    confidence = risk_state.get("confidence", 1.0)
    reasons = risk_state.get("reasons", [])
    trends = risk_state.get("trends", {})

    worsening = any(r in reasons for r in [
        "worsening_heart_rate",
        "falling_blood_pressure",
        "rising_troponin_trend",
        "rising_ck_mb_trend"
    ])

    # -------- Hard capacity constraint --------
    if pressure >= 0.9:
        return "BLOCK", "Hospital at critical capacity"

    # -------- Critical risk handling --------
    if risk_level == "CRITICAL":
        if resource_state["icu_full"]:
            return "ESCALATE", "Critical risk with ICU unavailable"
        return "PRIORITIZE", "Critical patient prioritized"

    # -------- High risk handling --------
    if risk_level == "HIGH":
        if worsening and confidence >= 0.8:
            return "PRIORITIZE", "High risk with worsening trends"

        if pressure >= 0.75:
            return "DELAY", "High risk but system overloaded"

        return "ALLOW", "High risk, resources available"

    # -------- Moderate risk handling --------
    if risk_level == "MODERATE":
        if worsening:
            return "OBSERVE", "Moderate risk with early deterioration"
        return "ALLOW", "Moderate risk stable"

    # -------- Low risk handling --------
    return "OBSERVE", "Risk stable"
