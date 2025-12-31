
"""
MCP Execution + Evaluator Workflow (HTTP-based, Windows-safe)

Responsibilities:
- Connect to a RUNNING OpenSCAD MCP server over HTTP
- Execute OpenSCAD code via MCP tools
- Robustly extract render image (base64) from MCP tool output
- Export STL
- Evaluate semantic + visual correctness using a multimodal LLM
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

evaluator_model = init_chat_model(model="gpt-4o")


# =============================================================================
# MCP CLIENT
# =============================================================================

_MCP_CLIENT: MultiServerMCPClient | None = None


def get_mcp_client() -> MultiServerMCPClient:
    global _MCP_CLIENT
    if _MCP_CLIENT is None:
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
# NORMALIZE MCP RENDER OUTPUT  ✅ FIXED
# =============================================================================

def extract_base64_image(render_result) -> str:
    """
    Normalize MCP render output to raw base64 image.
    Compatible with FastMCP + your OpenSCAD server.
    """

    # Step 1: unwrap list
    if isinstance(render_result, list):
        if not render_result:
            raise RuntimeError("Empty render result from MCP")
        render_result = render_result[0]

    # Step 2: unwrap dict (FastMCP tool response)
    if isinstance(render_result, dict):
        if "text" in render_result:
            render_result = render_result["text"]
        else:
            raise RuntimeError(f"Unexpected render dict: {render_result}")

    # Step 3: must be string now
    if not isinstance(render_result, str):
        raise RuntimeError(
            f"Unsupported render output type: {type(render_result)}"
        )

    # Step 4: must be data URL
    if not render_result.startswith("data:image/png;base64,"):
        raise RuntimeError(f"Render failed: {render_result[:200]}")

    # Step 5: strip prefix
    return render_result.split(",", 1)[1]


# =============================================================================
# MCP EXECUTION NODE
# =============================================================================

async def run_openscad_mcp(
    state: MCPEvalState,
) -> Command[Literal["evaluator"]]:

    try:
        client = get_mcp_client()
        tools = await client.get_tools()
        tools_by_name = {tool.name: tool for tool in tools}

        # 1. Write OpenSCAD script
        await tools_by_name["create_openscad_script"].ainvoke(
            {"script_content": state["openscad_code"]}
        )

        # 2. Save script
        await tools_by_name["save_openscad_script"].ainvoke(
            {"filename": "model.scad"}
        )

        # 3. Render image
        raw_render = await tools_by_name["view_render"].ainvoke(
            {"view": "isometric"}
        )
        render_image = extract_base64_image(raw_render)

        # 4. Export STL
        raw_stl = await tools_by_name["export_model_to_stl"].ainvoke(
            {"filename": "model"}
        )

        if isinstance(raw_stl, list):
            raw_stl = raw_stl[0] if raw_stl else None

        stl_path = None
        if isinstance(raw_stl, str) and "to" in raw_stl:
            stl_path = raw_stl.split("to", 1)[1].split("(")[0].strip()

    except Exception as e:
        logging.exception("MCP execution failed")
        raise CustomException(e, sys)

    return Command(
        update={
            "render_image": render_image,
            "stl_path": stl_path,
            "execution_logs": "OpenSCAD MCP execution successful",
        },
        goto="evaluator",
    )


# =============================================================================
# EVALUATOR NODE (MULTIMODAL)
# =============================================================================

async def evaluator(
    state: MCPEvalState,
) -> Command[Literal["__end__"]]:

    if not state.get("render_image"):
        raise CustomException("Missing render image", sys)

    messages = [
        SystemMessage(
            content=(
                "You are a CAD evaluator.\n"
                "You MUST analyze the provided render image.\n"
                "Describe the geometry and conclude PASS or FAIL."
            )
        ),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": f"OpenSCAD Code:\n{state['openscad_code']}",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{state['render_image']}"
                    },
                },
            ]
        ),
    ]

    response = await evaluator_model.ainvoke(messages)
    status = "pass" if "pass" in response.content.lower() else "fail"

    return Command(
        update={
            "evaluation_status": status,
            "evaluation_feedback": response.content,
            "iteration": state["iteration"] + 1,
        },
        goto=END,
    )


# =============================================================================
# GRAPH
# =============================================================================

builder = StateGraph(MCPEvalState)
builder.add_node("mcp_execution", run_openscad_mcp)
builder.add_node("evaluator", evaluator)

builder.add_edge(START, "mcp_execution")
builder.add_edge("mcp_execution", "evaluator")

mcp_eval_workflow = builder.compile()
