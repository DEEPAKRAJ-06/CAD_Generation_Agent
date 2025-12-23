
"""
Design Planning Workflow (CAD).

This module implements Step-2 of the agentic CAD workflow:
1. Generate a high-level, human-readable design plan
2. Present the plan for human approval
3. Loop until approval is granted

Architecture mirrors design_intent_workflow and deep_research scoping patterns.
"""

from typing_extensions import Literal
import sys

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from cad_agent_from_scratch.design_planning_state import (
    DesignPlanningState,
    PlanDesignIntent,
)

from cad_agent_from_scratch.prompts import (
    PLAN_DESIGN_INTENT_PROMPT,
)

from cad_agent_from_scratch.logger import logging
from cad_agent_from_scratch.exception import CustomException

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

model = init_chat_model(
    model="gpt-4.1-mini",
    temperature=0.0,
)

logging.info("Initialized CAD design planning workflow model")

# =============================================================================
# WORKFLOW NODES
# =============================================================================

def generate_design_plan(
    state: DesignPlanningState,
) -> Command[Literal["check_human_approval"]]:
    """
    Generate a high-level CAD design plan from clarified intent.
    """

    logging.info("Entered node: generate_design_plan")

    design_intent = state.get("design_intent")
    parsed_intent = state.get("parsed_intent")
    human_feedback = state.get("human_feedback")

    try:
        structured_model = model.with_structured_output(PlanDesignIntent)

        prompt_text = PLAN_DESIGN_INTENT_PROMPT.format(
            design_intent=design_intent,
            parsed_intent=parsed_intent,
            human_feedback=human_feedback or "None"
        )

        logging.debug(f"Planning prompt:\n{prompt_text}")

        response = structured_model.invoke(
            [HumanMessage(content=prompt_text)]
        )

        logging.info("Design plan generated successfully")
        logging.debug(f"Planning response object: {response}")

    except Exception as e:
        logging.exception("Error during generate_design_plan LLM call")
        raise CustomException(e, sys)

    return Command(
        goto="check_human_approval",
        update={
            "design_plan": response.design_plan,
            "plan_messages": [AIMessage(content=response.design_plan)],
        },
    )


def check_human_approval(
    state: DesignPlanningState,
) -> Command[Literal["generate_design_plan", "__end__"]]:
    """
    Decide whether to proceed or refine the design plan based on human approval.
    """

    logging.info("Entered node: check_human_approval")

    approved = state.get("human_approved", False)

    if approved:
        logging.info("Human approved the design plan — exiting planning workflow")
        return Command(goto=END)

    logging.info("Design plan not approved — looping back to planner")
    return Command(goto="generate_design_plan")

# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

logging.info("Building LangGraph for design planning workflow")

builder = StateGraph(DesignPlanningState)

builder.add_node("generate_design_plan", generate_design_plan)
builder.add_node("check_human_approval", check_human_approval)

builder.add_edge(START, "generate_design_plan")
builder.add_edge("generate_design_plan", "check_human_approval")

design_planning_workflow = builder.compile()

logging.info("Design planning workflow compiled successfully")
