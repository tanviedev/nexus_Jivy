def compute_pressure(state_row, static_row):
    icu_ratio = state_row["icu_beds_occupied"] / static_row["icu_beds_total"]
    ward_ratio = state_row["ward_beds_occupied"] / static_row["ward_beds_total"]

    pressure = (
        0.6 * icu_ratio +
        0.4 * ward_ratio
    )

    return round(min(pressure, 1.0), 2)
