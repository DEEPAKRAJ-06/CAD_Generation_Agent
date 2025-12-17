
"""State Definitions and Pydantic Schemas for CAD Design Intention Clarification.

This module defines the state objects and structured schemas used for
the design intention clarification step of an agentic CAD workflow.

The state manages conversation context, evolving design intent,
and parsed design parameters for downstream CAD agents.
"""

from typing_extensions import Optional, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


# ===== STATE DEFINITIONS =====

class AgentInputState(MessagesState):
    """
    Input state for the CAD agent.

    This state contains only the messages provided by the user
    and serves as the entry point for the intention clarification workflow.
    """
    pass


class DesignIntentState(MessagesState):
    """
    Main state for the design intention clarification workflow.

    Extends MessagesState with additional fields required to:
    - Track evolving design intent
    - Decide whether further clarification is required
    - Store the finalized design intent
    - Store parsed design parameters for downstream agents
    """

    # Human-readable, refined design intent summary
    design_intent: Optional[str]

    # Structured representation of the design intent (output of parser node)
    parsed_intent: Optional[dict]

    # Whether the agent has determined that clarification is still required
    needs_clarification: bool = True

    # Messages exchanged during the clarification loop
    clarification_messages: Annotated[Sequence[BaseMessage], add_messages]


# ===== STRUCTURED OUTPUT SCHEMAS =====

class ClarifyDesignIntent(BaseModel):
    """
    Schema used by the CAD agent to determine whether the
    current design request requires further clarification.
    """

    need_clarification: bool = Field(
        description="Whether the current design intent is underspecified for CAD generation.",
    )

    question: str = Field(
        description="A concise clarification question to ask the user if clarification is required.",
    )

    summary: str = Field(
        description="A concise summary of the finalized design intent if sufficient information is available.",
    )

# ===== PARSER SCHEMA =====

class ParsedDesignIntent(BaseModel):
    """Structured representation of a clarified CAD design intent."""

    object_name: str = Field(
        description="Name of the object being designed (e.g., airplane, bracket, gear)."
    )

    components: Optional[list[str]] = Field(
        description="Major components explicitly mentioned by the user."
    )

    dimensions: Optional[dict[str, str]] = Field(
        description="Dimensions mentioned in the design intent with units preserved as text."
    )

    configuration: Optional[str] = Field(
        description="High-level configuration or style (e.g., T-tail, angular body)."
    )

    assumptions: Optional[list[str]] = Field(
        description="Explicit assumptions made due to missing information."
    )
