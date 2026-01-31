import pandas as pd

# -------------------------
# Load baseline results
# -------------------------
baseline_df = pd.read_csv("data/baseline_output.csv")

# -------------------------
# Create evaluator-facing table
# -------------------------
presentation_table = baseline_df.rename(columns={
    "patient_id": "Patient ID",
    "timestamp": "Snapshot Time",
    "risk_level": "Risk Level",
    "decision": "Baseline Decision",
    "explanation": "Reason (Static)"
})

# -------------------------
# Select & order columns explicitly
# -------------------------
presentation_table = presentation_table[
    [
        "Patient ID",
        "Snapshot Time",
        "Risk Level",
        "Baseline Decision",
        "Reason (Static)"
    ]
]

# -------------------------
# Save evaluator-facing output
# -------------------------
presentation_table.to_csv(
    "data/baseline_decision_summary.csv",
    index=False
)

# -------------------------
# Optional: pretty print to console
# -------------------------
print("\nBaseline: Static Snapshot-Based Care Escalation Decisions\n")
print(presentation_table.to_string(index=False))
print("\nSaved to data/baseline_decision_summary.csv")
