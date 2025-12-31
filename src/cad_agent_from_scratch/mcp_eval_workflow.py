
"""
MCP Execution + Evaluator Workflow (HTTP-based, Windows-safe)

Responsibilities:
- Connect to a RUNNING OpenSCAD MCP server over HTTP
- Execute OpenSCAD code via MCP tools
- Capture render image, STL path, and logs
- Evaluate semantic correctness using an LLM
- Return structured feedback for optimizer loop

IMPORTANT:
- MCP server MUST already be running:
  uv run --with fastmcp fastmcp run main.py --transport http --host 127.0.0.1 --port 8000
- This workflow ONLY connects via HTTP
"""

import sys
from typing_extensions import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from langchain_mcp_adapters.client import MultiServerMCPClient

from cad_agent_from_scratch.mcp_eval_state import MCPEvalState
from cad_agent_from_scratch.logger import logging
from cad_agent_from_scratch.exception import CustomException

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

evaluator_model = init_chat_model(model="gpt-4.1")
logging.info("Initialized MCP evaluator model (HTTP mode)")

# =============================================================================
# MCP CLIENT (HTTP ONLY — NO PROCESS SPAWN)
# =============================================================================

_MCP_CLIENT: MultiServerMCPClient | None = None


def get_mcp_client() -> MultiServerMCPClient:
    """
    Create a singleton HTTP MCP client.
    This does NOT spawn subprocesses.
    """
    global _MCP_CLIENT

    if _MCP_CLIENT is None:
        logging.info("Creating MultiServerMCPClient (HTTP)")

        _MCP_CLIENT = MultiServerMCPClient(
            {
                "openscad": {
                    "transport": "http",
                    "url": "http://127.0.0.1:8000/mcp",
                }
            }
        )

    return _MCP_CLIENT


# =============================================================================
# MCP EXECUTION NODE
# =============================================================================

async def run_openscad_mcp(
    state: MCPEvalState,
) -> Command[Literal["evaluator"]]:

    logging.info("Entered node: run_openscad_mcp")

    try:
        client = get_mcp_client()

        # Discover tools exposed by MCP
        tools = await client.get_tools()
        tools_by_name = {tool.name: tool for tool in tools}

        logging.info(f"Available MCP tools: {list(tools_by_name.keys())}")

        # ---------------------------------------------------------------------
        # 1. Create / update OpenSCAD script
        # ---------------------------------------------------------------------
        await tools_by_name["create_openscad_script"].ainvoke(
            {"script_content": state["openscad_code"]}
        )

        # ---------------------------------------------------------------------
        # 2. Save script
        # ---------------------------------------------------------------------
        await tools_by_name["save_openscad_script"].ainvoke(
            {"filename": "model.scad"}
        )

        # ---------------------------------------------------------------------
        # 3. Render image (MCP RETURNS A LIST)
        # ---------------------------------------------------------------------
        render_results = await tools_by_name["view_render"].ainvoke(
            {"view": "isometric"}
        )

        render_image = None
        if isinstance(render_results, list) and len(render_results) > 0:
            render_image = render_results[0].get("image_base64")

        # ---------------------------------------------------------------------
        # 4. Export STL (MCP RETURNS A LIST)
        # ---------------------------------------------------------------------
        stl_results = await tools_by_name["export_model_to_stl"].ainvoke(
            {"filename": "model"}
        )

        stl_path = None
        if isinstance(stl_results, list) and len(stl_results) > 0:
            stl_path = stl_results[0].get("file_path")

        logging.info("OpenSCAD execution completed via MCP")

    except Exception as e:
        logging.exception("Error during MCP execution")
        raise CustomException(e, sys)

    return Command(
        update={
            "render_image": render_image,
            "stl_path": stl_path,
            "execution_logs": "OpenSCAD MCP execution completed successfully",
        },
        goto="evaluator",
    )


# =============================================================================
# EVALUATOR NODE (LLM JUDGE — NOT OPTIMIZER)
# =============================================================================

async def evaluator(
    state: MCPEvalState,
) -> Command[Literal["__end__"]]:

    logging.info("Entered node: evaluator")

    try:
        messages = [
            SystemMessage(
                content=(
                    "You are a CAD evaluator.\n"
                    "Check whether the OpenSCAD output matches the intended design.\n\n"
                    "Reply clearly whether it is correct or incorrect, with reasoning."
                )
            ),
            HumanMessage(
                content=(
                    f"OPENSCAD CODE:\n{state['openscad_code']}\n\n"
                    f"EXECUTION LOGS:\n{state['execution_logs']}\n\n"
                    f"STL PATH:\n{state['stl_path']}\n\n"
                    f"RENDER IMAGE (base64):\n{state['render_image']}"
                )
            ),
        ]

        response = await evaluator_model.ainvoke(messages)

        logging.info("Evaluator response received")
        logging.debug(response.content)

        status = "pass" if "correct" in response.content.lower() else "fail"

    except Exception as e:
        logging.exception("Error during evaluation")
        raise CustomException(e, sys)

    return Command(
        update={
            "evaluator_messages": [response],
            "evaluation_status": status,
            "evaluation_feedback": response.content,
            "iteration": state["iteration"] + 1,
        },
        goto=END,
    )


# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

logging.info("Building MCP evaluation workflow graph")

builder = StateGraph(MCPEvalState)

builder.add_node("mcp_execution", run_openscad_mcp)
builder.add_node("evaluator", evaluator)

builder.add_edge(START, "mcp_execution")
builder.add_edge("mcp_execution", "evaluator")

mcp_eval_workflow = builder.compile()

logging.info("MCP evaluation workflow compiled successfully")
