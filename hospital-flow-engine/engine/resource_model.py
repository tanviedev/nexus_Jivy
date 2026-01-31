import pandas as pd

class HospitalResourceModel:
    def __init__(self, static_path, state_path):
        self.static = pd.read_csv(static_path)
        self.state = pd.read_csv(state_path, parse_dates=["timestamp"])

        self._validate()

    def _validate(self):
        merged = self.state.merge(
            self.static,
            on="hospital_id",
            how="left"
        )

        errors = []

        if (merged["icu_beds_occupied"] > merged["icu_beds_total"]).any():
            errors.append("ICU occupancy exceeds total")

        if (merged["ward_beds_occupied"] > merged["ward_beds_total"]).any():
            errors.append("Ward occupancy exceeds total")

        if errors:
            raise ValueError(f"Data integrity error: {errors}")

    def get_latest_state(self, hospital_id):
        return (
            self.state[self.state["hospital_id"] == hospital_id]
            .sort_values("timestamp")
            .iloc[-1]
        )

    def get_static(self, hospital_id):
        return self.static[self.static["hospital_id"] == hospital_id].iloc[0]
