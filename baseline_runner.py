import pandas as pd
import json

# -------------------------
# Load data
# -------------------------
patients = pd.read_csv("data/patient_snapshot.csv")
hospital = pd.read_csv("data/hospital_snapshot.csv")

with open("config/baseline_risk_rules.json") as f:
    RISK_RULES = json.load(f)

with open("config/baseline_decision_map.json") as f:
    DECISION_MAP = json.load(f)

# -------------------------
# Risk scoring (static)
# -------------------------
def compute_risk(row):
    if (
        row["spo2"] < 90
        or row["heart_rate"] > 120
        or row["systolic_bp"] < 90
    ):
        return "HIGH"

    if (
        90 <= row["spo2"] <= 94
        or 100 <= row["heart_rate"] <= 120
    ):
        return "MEDIUM"

    return "LOW"


# -------------------------
# Decision logic (static)
# -------------------------
def decide_action(risk, icu_beds):
    action = DECISION_MAP[risk]

    if action == "ESCALATE" and icu_beds == 0:
        return "PRIORITIZE"

    return action


# -------------------------
# Run baseline
# -------------------------
outputs = []

for _, row in patients.iterrows():
    timestamp = row["timestamp"]
    hosp_state = hospital[hospital["timestamp"] == timestamp].iloc[0]

    risk = compute_risk(row)
    decision = decide_action(risk, hosp_state["icu_beds_available"])

    explanation = f"{decision} due to {risk} risk at snapshot"

    outputs.append({
        "patient_id": row["patient_id"],
        "timestamp": timestamp,
        "risk_level": risk,
        "decision": decision,
        "explanation": explanation
    })

# -------------------------
# Save output
# -------------------------
output_df = pd.DataFrame(outputs)
output_df.to_csv("data/baseline_output.csv", index=False)

print("Baseline decisions generated successfully.")
