import pandas as pd
from engine.resource_model import HospitalResourceModel
from engine.pressure_engine import compute_pressure
from engine.decision_engine import decide

STATIC = "data/hospital_static.csv"
STATE = "data/hospital_state.csv"
PATIENTS = "data/patient_stream.csv"

model = HospitalResourceModel(STATIC, STATE)
patients = pd.read_csv(PATIENTS, parse_dates=["arrival_time"])

decision_log = []

for _, patient in patients.sort_values("arrival_time").iterrows():

    # naive assignment (nearest / preferred later)
    hospital_id = model.static.sample(1).iloc[0]["hospital_id"]

    state = model.get_latest_state(hospital_id)
    static = model.get_static(hospital_id)

    pressure = compute_pressure(state, static)

    decision, score, reason = decide(
        patient,
        state,
        static,
        pressure
    )

    decision_log.append({
        "timestamp": patient["arrival_time"],
        "patient_id": patient["patient_id"],
        "hospital_id": hospital_id,
        "decision": decision,
        "pressure_score": score,
        "reason": reason
    })

df = pd.DataFrame(decision_log)
df.to_csv("data/decision_log.csv", index=False)

print("Simulation complete.")
