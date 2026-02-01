from reasoning.llm import llm


def analysis_chain(simulation_record: dict):
    """
    Analyzes a single simulation outcome.
    """

    prompt = f"""
    You are analyzing the output of a hospital flow simulation.

    Simulation record:
    {simulation_record}

    Instructions:
    - Identify the main drivers of the decision
    - Explain how risk level and hospital pressure interacted
    - Distinguish model output from rule-based logic
    - Do NOT recommend alternative actions
    - Do NOT invent new data
    """

    return llm.invoke(prompt).content
