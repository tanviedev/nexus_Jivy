from reasoning.analysis_chain import analysis_chain
from reasoning.explanation_chain import explanation_chain


def explain_simulation_output(simulation_record: dict, audience: str):
    """
    Runs reasoning strictly AFTER simulation output is known.
    """

    analysis = analysis_chain(simulation_record)

    explanation = explanation_chain(
        analysis=analysis,
        audience=audience
    )

    return explanation
