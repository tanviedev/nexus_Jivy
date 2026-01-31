import pandas as pd

class HospitalResourceModel:
    def __init__(self, static_path, state_path):
        self.static = pd.read_csv(static_path)
        self.state = pd.read_csv(state_path, parse_dates=["timestamp"])
        self._validate()

    def _validate(self):
        if (self.state["icu_beds_occupied"] > self.static["icu_beds_total"].iloc[0]).any():
            raise ValueError("ICU occupancy exceeds total capacity")

        if (self.state["ward_beds_occupied"] > self.static["ward_beds_total"].iloc[0]).any():
            raise ValueError("Ward occupancy exceeds total capacity")

    def get_latest_state(self):
        return self.state.sort_values("timestamp").iloc[-1]

    def get_static(self):
        return self.static.iloc[0]

    @staticmethod
    def build_resource_state(hospital_state, hospital_static, pressure):
        return {
            "pressure": pressure,
            "icu_full": hospital_state["icu_beds_occupied"] >= hospital_static["icu_beds_total"],
            "ward_full": hospital_state["ward_beds_occupied"] >= hospital_static["ward_beds_total"]
        }
