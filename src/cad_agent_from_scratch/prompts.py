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

--------------------------------------------------
RESPONSE FORMAT (STRICT)
--------------------------------------------------

Respond in valid JSON with EXACTLY these keys:

- "need_clarification": boolean
- "question": string
- "summary": string

If clarification is required, return:
{
  "need_clarification": true,
  "question": "<batched clarification questions>",
  "summary": ""
}

If no clarification is required, return:
{
  "need_clarification": false,
  "question": "",
  "summary": "<finalized design intent including assumptions>"
}
"""


# ===== PARSER PROMPT =====

PARSE_DESIGN_INTENT_PROMPT = """
You are a CAD design assistant.

The following text is a finalized and clarified CAD design intent:

<DesignIntent>
{design_intent}
</DesignIntent>

Extract all explicitly stated design information into a structured format.

Rules:
- Do NOT invent dimensions or components.
- If information is not present, leave the field null.
- Preserve units exactly as written.
- Assumptions must be explicitly stated as assumptions.

Return valid JSON that matches the required schema exactly.
"""

CAD_CRITERIA_PROMPT = """
You are a CAD design intent evaluator.

Your task is to determine whether the parsed CAD design intent
captures the specific design criterion provided.

Criterion:
{criterion}

Parsed Design Intent:
{parsed_intent}

Judgment rules:
- CAPTURED if the criterion is explicitly present or clearly implied
- NOT CAPTURED if missing, vague, or contradicted
- Do NOT infer dimensions or components that are not present

Respond in structured form.
"""

CAD_HALLUCINATION_PROMPT = """
You are a CAD design auditor.

Check whether the parsed design intent introduces
any geometry, dimensions, components, or configurations
that were NOT explicitly stated by the user.

Parsed Design Intent:
{parsed_intent}

User Criteria:
{success_criteria}

PASS if no extra assumptions exist.
FAIL if any unstated features are introduced.
"""