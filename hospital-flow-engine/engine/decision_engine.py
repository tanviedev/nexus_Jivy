# engine/decision_engine.py

def decide(risk_state, resource_state):
    pressure = resource_state["pressure"]

    if pressure >= 0.9:
        return "BLOCK", "Hospital at critical capacity"

    if risk_state["risk_level"] == "CRITICAL":
        if resource_state["icu_full"]:
            return "ESCALATE", "Critical risk but ICU unavailable"
        return "PRIORITIZE", "Critical patient prioritized"

    if risk_state["risk_level"] == "HIGH":
        if pressure >= 0.75:
            return "DELAY", "High risk but system overloaded"
        return "ALLOW", "High risk, resources available"

    return "OBSERVE", "Risk stable"
