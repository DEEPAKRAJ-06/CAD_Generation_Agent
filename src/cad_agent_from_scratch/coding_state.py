
"""
State definitions for the Agentic CAD Coding workflow.

This state is used ONLY for the coding stage:
- Manager → Worker(s) → Synthesizer
"""

import operator
from typing_extensions import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CodingState(TypedDict):
    """
    Global state for the OpenSCAD code generation workflow.
    """

    # Messages exchanged with the coding manager (planning-to-coding reasoning)
    manager_messages: Annotated[Sequence[BaseMessage], add_messages]

    # Approved human-readable design plan (text only)
    design_plan: str

    # Parsed intent from intention clarification (read-only context)
    parsed_intent: dict

    # OpenSCAD code blocks produced by worker coder(s)
    # - Single element for part-level objects
    # - Multiple elements for assemblies
    worker_code_blocks: Annotated[list[str], operator.add]

    # Final synthesized OpenSCAD code (single valid file)
    final_openscad_code: str
