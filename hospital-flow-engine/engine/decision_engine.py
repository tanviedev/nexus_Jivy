def decide(patient, state, static, pressure):
    reasons = []

    if pressure >= 0.9:
        return "BLOCK", pressure, "Hospital at critical capacity"

    if patient["requires_icu"] == 1:
        if state["icu_beds_occupied"] >= static["icu_beds_total"]:
            return "ESCALATE", pressure, "ICU unavailable"

    if pressure >= 0.75:
        return "DELAY", pressure, "High operational pressure"

    if patient["severity_score"] >= 85 and pressure < 0.75:
        return "ALLOW", pressure, "High severity prioritized"

    return "ALLOW", pressure, "Capacity available"
