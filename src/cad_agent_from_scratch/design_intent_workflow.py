
"""
Design Intent Clarification and Parsing Workflow (CAD).

This module implements Step-1 of the agentic CAD workflow:
1. Determine whether the user's design request needs clarification
2. Produce a finalized design intent summary
3. Parse the finalized intent into structured CAD-ready parameters

Architecture mirrors deep_research_from_scratch scoping workflow.
"""

from datetime import datetime
from typing_extensions import Literal
import sys

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from cad_agent_from_scratch.design_intent_state import (
    DesignIntentState,
    AgentInputState,
    ClarifyDesignIntent,
    ParsedDesignIntent,
)

from cad_agent_from_scratch.prompts import (
    clarify_design_intent_instructions,
    PARSE_DESIGN_INTENT_PROMPT,
)

from cad_agent_from_scratch.logger import logging
from cad_agent_from_scratch.exception import CustomException

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

model = init_chat_model(
    model="gpt-4.1",
    temperature=0.0,
)

logging.info("Initialized CAD design intent workflow model")

# =============================================================================
# WORKFLOW NODES
# =============================================================================

def clarify_design_intent(
    state: DesignIntentState,
) -> Command[Literal["parse_design_intent", "__end__"]]:
    """
    Decide whether the user's design request is sufficiently specified.
    """

    logging.info("Entered node: clarify_design_intent")
    logging.debug(f"Incoming messages: {state.get('messages')}")

    try:
        structured_model = model.with_structured_output(ClarifyDesignIntent)

        prompt_text = clarify_design_intent_instructions.format(
            messages=get_buffer_string(state["messages"])
        )

        logging.debug(f"Clarification prompt:\n{prompt_text}")

        response = structured_model.invoke(
            [HumanMessage(content=prompt_text)]
        )

        logging.info("LLM clarification response received")
        logging.debug(f"Clarification response object: {response}")

    except Exception as e:
        logging.exception("Error during clarify_design_intent LLM call")
        raise CustomException(e, sys)

    if response.need_clarification:
        logging.info("Clarification required — returning question to user")

        return Command(
            goto=END,
            update={
                "needs_clarification": True,
                "messages": [AIMessage(content=response.question)],
            },
        )

    logging.info("Design intent sufficient — proceeding to parsing")

    return Command(
        goto="parse_design_intent",
        update={
            "needs_clarification": False,
            "design_intent": response.summary,
            "messages": [AIMessage(content=response.summary)],
        },
    )


def parse_design_intent(state: DesignIntentState):
    """
    Parse finalized design intent into structured CAD parameters.
    """

    logging.info("Entered node: parse_design_intent")
    design_intent = state.get("design_intent")
    logging.debug(f"Design intent text: {design_intent}")

    try:
        structured_parser = model.with_structured_output(ParsedDesignIntent)

        parse_prompt = PARSE_DESIGN_INTENT_PROMPT.format(
            design_intent=design_intent
        )

        logging.debug(f"Parsing prompt:\n{parse_prompt}")

        parsed = structured_parser.invoke(
            [HumanMessage(content=parse_prompt)]
        )

        logging.info("Design intent parsed successfully")
        logging.debug(f"Parsed intent object: {parsed}")

    except Exception as e:
        logging.exception("Error during parse_design_intent LLM call")
        raise CustomException(e, sys)

    return {
        "parsed_intent": parsed.model_dump()
    }

# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

logging.info("Building LangGraph for design intent workflow")

builder = StateGraph(
    DesignIntentState,
    input_schema=AgentInputState,
)

builder.add_node("clarify_design_intent", clarify_design_intent)
builder.add_node("parse_design_intent", parse_design_intent)

builder.add_edge(START, "clarify_design_intent")
builder.add_edge("parse_design_intent", END)

design_intent_workflow = builder.compile()

logging.info("Design intent workflow compiled successfully")
