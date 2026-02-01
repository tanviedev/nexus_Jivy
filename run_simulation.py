from hospital_flow_engine.simulate import run_simulation
from reasoning.post_simulation_chain import explain_simulation_output


def main():
    outputs = run_simulation()

    print("\n=== SIMULATION OUTPUTS (Final State per Patient) ===")
    for o in outputs:
        print(
            f"{o['timestamp']} | "
            f"Patient={o['patient_id']} | "
            f"Risk={o['risk_level']} | "
            f"Score={o['signal_score']} | "
            f"Decision={o['decision']} | "
            f"Why={o['engine_explanation']}"
        )

    # 🔁 Interactive loop
    while True:
        patient_id = input(
            "\nEnter patient ID to explain (e.g., P0119) or type 'exit': "
        ).strip()

        if patient_id.lower() == "exit":
            print("Exiting explanation loop.")
            break

        # Find matching patient record
        selected = next(
            (o for o in outputs if o["patient_id"] == patient_id),
            None
        )

        if not selected:
            print(f"No record found for patient {patient_id}")
            continue

        print("\n=== SELECTED OUTPUT FOR REASONING ===")
        print(selected)

        reasoning = explain_simulation_output(
            simulation_record=selected,
            audience="doctor"
        )

        print("\n=== LANGCHAIN REASONING ===")
        print(reasoning)

        choice = input(
            "\nType '1' to analyze another patient or '2' to exit: "
        ).strip()

        if choice == "2":
            print("Session ended.")
            break


if __name__ == "__main__":
    main()
