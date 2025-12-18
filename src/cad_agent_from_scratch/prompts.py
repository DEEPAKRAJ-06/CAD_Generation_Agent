"""
Prompt templates for the Agentic CAD Generation system.

This module contains all prompt templates used across the CAD workflow,
including:
- Design intention clarification
- Design intent parsing
- Evaluation and hallucination checks

IMPORTANT:
All prompts are structured-output safe.
NO raw JSON objects are shown in prompts.
"""

# =============================================================================
# DESIGN INTENT CLARIFICATION PROMPT
# =============================================================================

clarify_design_intent_instructions = """
These are the messages exchanged so far between the user and the CAD assistant:

<Messages>
{messages}
</Messages>

Your task is to determine whether the user's design request is sufficiently
specified to BEGIN coarse CAD model generation.

IMPORTANT GOAL:
You are NOT completing the design.
You are ONLY deciding whether enough information exists to safely proceed.

A design request is considered SUFFICIENT if:
- The object type is clear (e.g., cube, airplane, bracket)
- Approximate size or scale is known (explicit or implicit)
- High-level configuration or style is defined
- It is clear whether the model is static or movable
- Major components are identified (if applicable)

You MUST NOT attempt to:
- Refine detailed proportions
- Infer precise dimensions
- Add cosmetic or aesthetic assumptions

--------------------------------------------------
CLARIFICATION STRATEGY
--------------------------------------------------

If clarification is required:
- Ask MULTIPLE related questions in ONE message
- Group questions logically
- Focus ONLY on blocking information
- Prefer approximate values or ranges
- Do NOT repeat already-answered questions

Stop asking questions if:
- Only secondary details remain
- Remaining uncertainty does not block coarse CAD generation

--------------------------------------------------
RESPONSE INSTRUCTIONS
--------------------------------------------------

Return values for the following fields ONLY:
- need_clarification
- question
- summary

Rules:
- need_clarification must be true or false
- question must contain clarification questions if needed, otherwise empty
- summary must contain the finalized design intent if sufficient, otherwise empty

Do NOT include explanations outside these fields.
"""

# =============================================================================
# DESIGN INTENT PARSING PROMPT
# =============================================================================

PARSE_DESIGN_INTENT_PROMPT = """
You are a CAD design assistant.

The text below represents a FINALIZED and CLARIFIED CAD design intent:

<DesignIntent>
{design_intent}
</DesignIntent>

Your task is to extract ONLY information that is explicitly stated.

Extraction rules:
- Do NOT invent geometry, dimensions, or components
- If information is missing, leave the field empty
- Preserve units exactly as written
- Any assumptions must be explicitly listed as assumptions

Populate the following fields:
- object_name
- components
- dimensions
- configuration
- assumptions

Return ONLY structured field values.
Do NOT add commentary or explanations.
"""

# =============================================================================
# CAD CRITERIA EVALUATION PROMPT
# =============================================================================

CAD_CRITERIA_PROMPT = """
You are a CAD design intent evaluator.

Your task is to determine whether the parsed design intent
captures the given criterion.

IMPORTANT:
- Not all criteria apply to all objects.
- Missing fields are acceptable if the criterion is not applicable.
- Do NOT penalize the design intent for being unrelated.

Criterion:
{criterion}

Parsed Design Intent:
{parsed_intent}

Evaluation rules:
1. CAPTURED:
   - The criterion is explicitly present, OR
   - The criterion is clearly implied by the parsed intent

2. NOT CAPTURED:
   - The criterion is relevant but missing, OR
   - The criterion contradicts the parsed intent

3. NOT APPLICABLE (treat as NOT CAPTURED):
   - The criterion does not apply to the object type
   - Example: airplane criteria for a cube

Reasoning guidelines:
- First identify the object type
- Decide whether the criterion applies
- Then decide capture status
- Never blame the parser

Return:
- is_captured: true or false
- reasoning: concise, CAD-grounded explanation
"""


# =============================================================================
# CAD HALLUCINATION CHECK PROMPT
# =============================================================================

CAD_HALLUCINATION_PROMPT = """
You are a CAD design auditor.

Check whether the parsed design intent introduces ANY information
not explicitly provided by the user.

Parsed Design Intent:
{parsed_intent}

User-Provided Criteria:
{success_criteria}

PASS if:
- No unstated dimensions, geometry, or components are introduced
- Any assumptions are explicitly labeled

FAIL if:
- New features, sizes, or configurations are invented
- Design choices are narrowed beyond user input

Return values for:
- no_hallucination
- reasoning
"""