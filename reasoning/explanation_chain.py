from reasoning.llm import llm


def explanation_chain(analysis: str, audience: str):
    """
    Converts technical analysis into a clear explanation.
    """

    prompt = f"""
    Explain the following analysis to a {audience}.

    Analysis:
    {analysis}

    Constraints:
    - Be clear and concise
    - Use domain-appropriate language
    - Avoid speculation
    - Clearly state uncertainty if present
    """

    return llm.invoke(prompt).content
