import pandas as pd
from pathlib import Path

from hospital_flow_engine.engine.risk_engine import RiskAgent
from hospital_flow_engine.engine.pressure_engine import compute_pressure
from hospital_flow_engine.engine.decision_engine import decide
from hospital_flow_engine.engine.resource_model import HospitalResourceModel


# ------------------------------------------------------------------
# CORRECT path resolution (FINAL)
# simulate.py → hospital_flow_engine/ → data/
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent      # hospital_flow_engine/
DATA_DIR = BASE_DIR / "data"                   # hospital_flow_engine/data



def run_simulation():
    """
    Runs the hospital flow simulation and returns structured outputs
    suitable for post-hoc reasoning.
    """

    # ---- Load patient data ----
    patients = pd.read_csv(DATA_DIR / "heart_attack_temporal_5steps.csv")
    patients["timestamp"] = pd.to_datetime(patients["timestamp"])

    # ---- Initialize models ----
    resource_model = HospitalResourceModel(
        static_path=DATA_DIR / "hospital_static_extended.csv",
        state_path=DATA_DIR / "hospital_state_extended.csv"
    )

    risk_agent = RiskAgent(window_size=5)

    outputs = []

    # ---- Simulation loop ----
    for _, row in patients.iterrows():
        patient = row.to_dict()

        risk_agent.observe(patient)
        risk_state = risk_agent.update(patient["patient_id"])

        if risk_state is None:
            continue

        hospital_state = resource_model.get_latest_state()
        hospital_static = resource_model.get_static()

        pressure = compute_pressure(hospital_state, hospital_static)

        resource_state = HospitalResourceModel.build_resource_state(
            hospital_state,
            hospital_static,
            pressure
        )

        decision, explanation = decide(risk_state, resource_state)

        record = {
            "timestamp": patient["timestamp"],
            "patient_id": patient["patient_id"],
            "risk_level": risk_state["risk_level"],
            "signal_score": risk_state["signal_score"],
            "decision": decision,
            "engine_explanation": explanation,
            "pressure": pressure,
        }

        outputs.append(record)

    return outputs
