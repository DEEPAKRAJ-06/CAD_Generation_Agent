
"""
State definitions for MCP execution and evaluation loop.

This state is used AFTER coding and BEFORE final acceptance.
"""

import operator
from typing_extensions import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class MCPEvalState(TypedDict):
    """
    State for OpenSCAD MCP execution + evaluator–optimizer loop.
    """

    # Intended design (semantic ground truth)
    design_plan: str

    # Final OpenSCAD code from coding workflow
    openscad_code: str

    # MCP execution artifacts
    render_image: str | None
    stl_path: str | None
    execution_logs: str | None

    # Evaluator reasoning messages
    evaluator_messages: Annotated[Sequence[BaseMessage], add_messages]

    # Structured evaluator feedback
    evaluation_status: str | None   # "pass" | "fail"
    evaluation_feedback: str | None

    # Loop control
    iteration: int
    max_iterations: int
