
"""
State Definitions and Pydantic Schemas for CAD Design Planning.

This module defines the state extensions and structured schemas used for
the Planning step of an agentic CAD workflow.

Responsibilities:
- Extend the shared CAD state with planning artifacts
- Define structured LLM output schemas for design planning
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

logging.info("Loaded design_planning_state module")

# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class DesignPlanningState(MessagesState):
    """
    Extended state for the CAD design planning step.

    Builds on the clarified design intent and introduces:
    - A human-readable design plan
    - Human-in-the-loop approval signals
    - Iterative refinement support
    """

    # Human-readable, component-wise design plan
    design_plan: Optional[str]

    # Messages exchanged during planning refinements
    plan_messages: Annotated[Sequence[BaseMessage], add_messages]

    # Human approval flag (controls progression to coding)
    human_approved: bool = False

    # Optional human feedback when plan is rejected
    human_feedback: Optional[str]


logging.info("Registered DesignPlanningState")

# =============================================================================
# STRUCTURED OUTPUT SCHEMAS (LLM)
# =============================================================================

class PlanDesignIntent(BaseModel):
    """
    Schema used by the Planning agent to propose a CAD design plan.

    The plan must be:
    - Human-readable
    - Component-wise
    - Approximate and semantic
    - Free of implementation details
    """

    design_plan: str = Field(
        description=(
            "A clear, human-readable, component-wise CAD design plan. "
            "Must describe major components, approximate proportions, and "
            "high-level structure. No code, no coordinates, no primitives."
        )
    )

    ready_for_review: bool = Field(
        description=(
            "Whether the generated plan is ready for human review and approval."
        )
    )


logging.info("Registered PlanDesignIntent schema")
