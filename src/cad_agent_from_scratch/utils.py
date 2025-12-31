from langchain_core.tools import tool

@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """
    Tool for strategic reflection and decision-making.

    Use this tool to explicitly record reasoning before making
    important decisions in agent workflows.

    Args:
        reflection: Detailed reasoning about structure, risks, and next steps.

    Returns:
        Confirmation that reflection was recorded.
    """
    return f"Reflection recorded: {reflection}"