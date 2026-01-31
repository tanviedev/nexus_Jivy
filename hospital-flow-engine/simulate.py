# import pandas as pd

# from engine.risk_engine import RiskAgent
# from engine.pressure_engine import compute_pressure
# from engine.decision_engine import decide
# from engine.resource_model import HospitalResourceModel


# PATIENT_ID = input("Enter patient ID to monitor (e.g., P0001): ").strip()

# # -----------------------------
# # Load datasets
# # -----------------------------
# # patients = pd.read_csv("data/heart_attack_temporal_5steps.csv")

# # resource_model = HospitalResourceModel(
# #     static_path="data/hospital_static_extended.csv",
# #     state_path="data/hospital_state_extended.csv"
# # )

# # risk_agent = RiskAgent(window_size=5)



# patients = pd.read_csv("data/heart_attack_temporal_5steps.csv")

# # Validate patient ID
# if PATIENT_ID not in patients["patient_id"].unique():
#     raise ValueError(f"Patient ID {PATIENT_ID} not found in dataset.")

# # Filter to single patient and sort by time
# patients = patients[patients["patient_id"] == PATIENT_ID]
# patients = patients.sort_values("timestamp")


# #HOSPITAL_ID = 1  # choose a hospital to simulate

# risk_agent = RiskAgent(window_size=1)

# resource_model = HospitalResourceModel(
#     static_path="data/hospital_static_extended.csv",
#     state_path="data/hospital_state_extended.csv"
# )

# # -----------------------------
# # Simulation loop
# # -----------------------------
# for _, row in patients.iterrows():
#     patient = row.to_dict()

#     print("Processing", patient["patient_id"])


#     # ---- Risk Agent ----
#     risk_agent.observe(patient)
#     risk_state = risk_agent.update(patient["patient_id"])

#     if risk_state is None:
#         continue  # not enough temporal data yet

#     # ---- Resource Agent ----
#     hospital_state = resource_model.get_latest_state()
#     hospital_static = resource_model.get_static()

#     pressure = compute_pressure(hospital_state, hospital_static)

#     resource_state = HospitalResourceModel.build_resource_state(
#         hospital_state,
#         hospital_static,
#         pressure
#     )

#     # ---- Decision Engine ----
#     decision, explanation = decide(risk_state, resource_state)

#     print(
#         f"[{patient['timestamp']}] "
#         f"Patient {patient['patient_id']} | "
#         f"Risk={risk_state['risk_level']} | "
#         f"Decision={decision} | "
#         f"Why={explanation}"
#     )




import pandas as pd

from engine.risk_engine import RiskAgent
from engine.pressure_engine import compute_pressure
from engine.decision_engine import decide
from engine.resource_model import HospitalResourceModel

# -----------------------------
# Load datasets
# -----------------------------
patients = pd.read_csv("data/heart_attack_temporal_5steps.csv")

# 🔴 IMPORTANT: ensure timestamp is datetime
patients["timestamp"] = pd.to_datetime(patients["timestamp"])

resource_model = HospitalResourceModel(
    static_path="data/hospital_static_extended.csv",
    state_path="data/hospital_state_extended.csv"
)

risk_agent = RiskAgent(window_size=5)

# -----------------------------
# Simulation loop
# -----------------------------
for _, row in patients.iterrows():
    patient = row.to_dict()

    print(f"\nProcessing patient {patient['patient_id']}")

    # ---- Risk Agent ----
    risk_agent.observe(patient)
    risk_state = risk_agent.update(patient["patient_id"])

    if risk_state is None:
        continue  # not enough temporal data yet

    # ---- Resource Agent ----
    hospital_state = resource_model.get_latest_state()
    hospital_static = resource_model.get_static()

    pressure = compute_pressure(hospital_state, hospital_static)

    resource_state = HospitalResourceModel.build_resource_state(
        hospital_state,
        hospital_static,
        pressure
    )

    # ---- Decision Engine ----
    decision, explanation = decide(risk_state, resource_state)

    print(
        f"[{patient['timestamp']}] | "
        f"Risk={risk_state['risk_level']} | "
        f"Score={risk_state['signal_score']} | "
        f"Decision={decision} | "
        f"Why={explanation}"
    )
