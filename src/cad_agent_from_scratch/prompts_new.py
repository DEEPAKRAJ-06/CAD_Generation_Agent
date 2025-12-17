# ===== CLARIFY DESIGN INTENT PROMPT =====

clarify_design_intent_instructions = """
These are the messages exchanged so far between the user and the CAD assistant:

<Messages>
{messages}
</Messages>

Your task is to determine whether the current design request contains
SUFFICIENT information to BEGIN CAD model generation.

IMPORTANT:
Your goal is NOT to fully specify the design.
Your goal is to collect enough information to safely hand off to the next CAD agent.

A design intent is considered SUFFICIENT if:
- The object type is clear
- The overall size is approximately defined
- The major configuration/style is defined
- The model is static or movable
- Major components are identified

Do NOT attempt to refine:
- Detailed proportions (e.g., chord length, airfoil shape)
- Manufacturing tolerances
- Secondary or cosmetic details

--------------------------------------------------
CLARIFICATION STRATEGY
--------------------------------------------------

If clarification is required:
- Ask MULTIPLE related questions in a SINGLE message.
- Group questions logically.
- Limit to ONLY the most critical missing information.
- Prefer ranges or approximate values.

Aim to finish clarification within 3–5 turns.
If some information is still missing after that, STOP asking questions
and proceed with reasonable assumptions.

--------------------------------------------------
WHEN TO STOP ASKING QUESTIONS
--------------------------------------------------

You MUST stop asking questions and proceed if:
- Only secondary details remain, OR
- Remaining unknowns will not block coarse CAD generation
"""


# ===== PARSER PROMPT =====

PARSE_DESIGN_INTENT_PROMPT = """
You are a CAD design assistant.

The following text is a finalized and clarified CAD design intent:

<DesignIntent>
{design_intent}
</DesignIntent>

Extract all explicitly stated design information into the structured format provided.

Rules:
- Do NOT invent dimensions or components.
- If information is not present, leave the field null.
- Preserve units exactly as written.
- Assumptions must be explicitly stated as assumptions.
"""