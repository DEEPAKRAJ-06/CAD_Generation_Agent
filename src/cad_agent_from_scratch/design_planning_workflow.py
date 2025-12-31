
"""
CAD Planning Sub-Agent (TypedDict-based).

Mirrors deep_research/research_agent.py exactly.
"""

from pydantic import BaseModel, Field

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command

from cad_agent_from_scratch.prompts import PLAN_DESIGN_INTENT_PROMPT
from cad_agent_from_scratch.design_planning_state import PlanningAgentState


# ---------------- MODEL ---------------- #

model = init_chat_model(
    model="gpt-4.1-mini",
    temperature=0.0,
)


# ---------------- SCHEMA ---------------- #

class PlanDesignIntent(BaseModel):
    design_plan: str = Field(...)
    ready_for_review: bool = Field(...)


# ---------------- NODES ---------------- #

def generate_plan(state: PlanningAgentState):
    # Safety guard against infinite loops
    if state.get("iterations", 0) >= 5:
        return END

    structured_model = model.with_structured_output(PlanDesignIntent)

    prompt = PLAN_DESIGN_INTENT_PROMPT.format(
        design_intent=state["design_intent"],
        parsed_intent=state["parsed_intent"],
        human_feedback=state.get("human_feedback") or "None",
    )

    response = structured_model.invoke(
        [HumanMessage(content=prompt)]
    )

    return {
        "design_plan": response.design_plan,
        "planner_messages": [AIMessage(content=response.design_plan)],
        "iterations": state.get("iterations", 0) + 1,
    }


def hitl_review(state: PlanningAgentState):
    request = {
        "action_request": {
            "action": "Review CAD Design Plan",
            "args": {},
        },
        "config": {
            "allow_accept": True,
            "allow_edit": True,
            "allow_ignore": True,
        },
        "description": state["design_plan"],
    }

    result = interrupt([request])[0]

    # ✅ ACCEPT → terminate
    if result["type"] == "accept":
        return Command(goto=END)

    # ✅ EDIT → store feedback AND loop back
    if result["type"] == "edit":
        return Command(
            goto="generate_plan",
            update={
                "human_feedback": result["args"]
            }
        )

    # ✅ IGNORE → terminate
    return Command(goto=END)


# ---------------- GRAPH ---------------- #

planning_builder = StateGraph(PlanningAgentState)

planning_builder.add_node("generate_plan", generate_plan)
planning_builder.add_node("hitl_review", hitl_review)

planning_builder.add_edge(START, "generate_plan")
planning_builder.add_edge("generate_plan", "hitl_review")
planning_builder.add_edge("hitl_review", "generate_plan")

planning_agent = planning_builder.compile()
