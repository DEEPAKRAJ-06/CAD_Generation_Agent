
"""
TypedDict-based state for the CAD Planning sub-agent.

This is an INTERNAL agent state (like research_agent.py),
NOT a LangGraph MessagesState.
"""

from typing_extensions import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class PlanningAgentState(TypedDict):
    # Inputs (copied from shared state)
    design_intent: str
    parsed_intent: dict

    # Planning loop
    planner_messages: Annotated[Sequence[BaseMessage], add_messages]
    human_feedback: Optional[str]
    iterations: int

    # Output
    design_plan: Optional[str]
