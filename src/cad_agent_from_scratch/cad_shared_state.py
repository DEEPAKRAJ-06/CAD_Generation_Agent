
"""
Shared State Definitions for the Agentic CAD Workflow.

This module defines a SINGLE shared LangGraph state used across
multiple workflow stages, including:
1. Design Intent Clarification & Parsing
2. Design Planning (Human-in-the-Loop)
3. Future CAD code generation and evaluation steps

Responsibilities:
- Provide a unified state schema across all agent stages
- Ensure state continuity when composing multiple LangGraph workflows
- Prevent state loss at workflow boundaries
"""

from typing_extensions import Optional, Annotated, Sequence

from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class CADSharedState(MessagesState):
    """
    Unified shared state for the CAD agent.

    This state is intentionally used by ALL workflow stages to
    avoid schema coercion and key loss when composing graphs.
    """

    # -----------------------------------------------------------------
    # Step 1: Design Intent Clarification & Parsing outputs
    # -----------------------------------------------------------------

    design_intent: Optional[str]
    parsed_intent: Optional[dict]
    needs_clarification: bool = True
    clarification_messages: Annotated[Sequence[BaseMessage], add_messages]

    # -----------------------------------------------------------------
    # Step 2: Design Planning (Human-in-the-Loop) outputs
    # -----------------------------------------------------------------

    design_plan: Optional[str]
    plan_messages: Annotated[Sequence[BaseMessage], add_messages]
    human_feedback: Optional[str]
