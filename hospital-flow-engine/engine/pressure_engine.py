def compute_pressure(state_row, static_row):
    icu_ratio = state_row["icu_beds_occupied"] / static_row["icu_beds_total"]
    ward_ratio = state_row["ward_beds_occupied"] / static_row["ward_beds_total"]

    pressure = (
        0.45 * icu_ratio +
        0.25 * ward_ratio +
        0.20 * state_row["staff_load"] +
        0.10 * min(state_row["er_queue_length"] / 20, 1)
    )

    return round(min(pressure, 1.0), 2)
