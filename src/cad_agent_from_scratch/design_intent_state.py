
"""
State Definitions and Pydantic Schemas for CAD Design Intention Clarification.

This module defines the state objects and structured schemas used for
the design intention clarification step of an agentic CAD workflow.

Responsibilities:
- Define LangGraph state containers
- Define structured LLM output schemas
- NO workflow logic
"""

from typing_extensions import Optional, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from cad_agent_from_scratch.logger import logging

# =============================================================================
# MODULE INIT LOG
# =============================================================================

logging.info("Loaded design_intent_state module")

# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class AgentInputState(MessagesState):
    """
    Input state for the CAD agent.

    Contains only messages provided by the user.
    Acts as the entry point for the design intent clarification workflow.
    """
    pass


class DesignIntentState(MessagesState):
    """
    Main state for the design intention clarification workflow.

    Extends MessagesState with fields to:
    - Track evolving design intent
    - Decide whether clarification is required
    - Store finalized design intent
    - Store parsed design parameters
    """

    design_intent: Optional[str]
    parsed_intent: Optional[dict]
    needs_clarification: bool = True
    clarification_messages: Annotated[Sequence[BaseMessage], add_messages]


logging.info("Registered DesignIntentState and AgentInputState")

# =============================================================================
# STRUCTURED OUTPUT SCHEMAS (LLM)
# =============================================================================

class ClarifyDesignIntent(BaseModel):
    """
    Schema used by the CAD agent to determine whether the
    current design request requires further clarification.
    """

    need_clarification: bool = Field(
        description="Whether the current design intent is underspecified for CAD generation."
    )
    question: str = Field(
        description="Clarification question(s) to ask the user if needed."
    )
    summary: str = Field(
        description="Finalized design intent summary if sufficient information is available."
    )


class ParsedDesignIntent(BaseModel):
    """
    Structured representation of a clarified CAD design intent.

    IMPORTANT SEMANTIC RULE:
    - If the object is atomic (e.g., cube, sphere, rod) and no sub-components
      are explicitly mentioned, `components` MUST contain a single item equal
      to `object_name` (e.g., ["cube"]).
    - `components` being empty or None must NEVER be interpreted as
      "no object exists".
    """

    object_name: str = Field(
        description="Name of the object being designed (e.g., cube, airplane, bracket)."
    )

    components: Optional[list[str]] = Field(
        description=(
            "List of major components explicitly mentioned by the user. "
            "For atomic objects, this MUST be a single-item list containing "
            "the object_name."
        )
    )

    dimensions: Optional[dict[str, str]] = Field(
        description="Dimensions mentioned in the design intent with units preserved as text."
    )

    configuration: Optional[str] = Field(
        description="High-level configuration or style (e.g., solid, hollow, T-tail)."
    )

    assumptions: Optional[list[str]] = Field(
        description="Explicit assumptions made due to missing information."
    )


logging.info("Registered ClarifyDesignIntent and ParsedDesignIntent schemas")
