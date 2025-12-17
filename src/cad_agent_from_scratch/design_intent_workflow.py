



from datetime import datetime
from typing_extensions import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langchain_core.prompts import PromptTemplate
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

# ===== MODEL =====

model = init_chat_model(
    model="gpt-4o-mini",
    temperature=0.0,
)

# ===== PROMPT TEMPLATES =====

clarify_prompt = PromptTemplate(
    template=clarify_design_intent_instructions,
    input_variables=["messages"],
)

parse_prompt = PromptTemplate(
    template=PARSE_DESIGN_INTENT_PROMPT,
    input_variables=["design_intent"],
)

# ===== WORKFLOW NODES =====

def clarify_design_intent(
    state: DesignIntentState,
) -> Command[Literal["parse_design_intent", "__end__"]]:

    structured_model = model.with_structured_output(ClarifyDesignIntent)

    response = structured_model.invoke([
        HumanMessage(
            content=clarify_prompt.format(
                messages=get_buffer_string(state["messages"])
            )
        )
    ])

    if response.need_clarification:
        return Command(
            goto=END,
            update={
                "needs_clarification": True,
                "messages": [AIMessage(content=response.question)],
            },
        )

    return Command(
        goto="parse_design_intent",
        update={
            "needs_clarification": False,
            "design_intent": response.summary,
            "messages": [AIMessage(content=response.summary)],
        },
    )


def parse_design_intent(state: DesignIntentState):
    structured_parser = model.with_structured_output(ParsedDesignIntent)

    parsed = structured_parser.invoke([
        HumanMessage(
            content=parse_prompt.format(
                design_intent=state["design_intent"]
            )
        )
    ])

    return {
        "parsed_intent": parsed.model_dump()
    }

# ===== GRAPH =====

builder = StateGraph(
    DesignIntentState,
    input_schema=AgentInputState,
)

builder.add_node("clarify_design_intent", clarify_design_intent)
builder.add_node("parse_design_intent", parse_design_intent)

builder.add_edge(START, "clarify_design_intent")
builder.add_edge("parse_design_intent", END)

design_intent_workflow = builder.compile()
