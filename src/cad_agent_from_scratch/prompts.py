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

# =============================================================================
# DESIGN PLANNING PROMPT
# =============================================================================

PLAN_DESIGN_INTENT_PROMPT = """
You are a CAD Planning Agent.

You are given a FINALIZED CAD design intent and its structured interpretation.
Your task is to produce a HIGH-LEVEL CAD DESIGN PLAN that will be reviewed and
approved by a human BEFORE any CAD code is written.

You are NOT designing geometry.
You are NOT inventing structure.
You are articulating a clear plan based strictly on the clarified intent.

--------------------------------------------------
INPUT CONTEXT
--------------------------------------------------

Finalized Design Intent (human-readable):
<DesignIntent>
{design_intent}
</DesignIntent>

Parsed Design Intent (structured, explicit facts only):
<ParsedIntent>
{parsed_intent}
</ParsedIntent>

Human Feedback (if any, from previous review):
<HumanFeedback>
{human_feedback}
</HumanFeedback>

If HumanFeedback is "None", generate the initial plan.
If HumanFeedback is present, revise the plan ONLY to address that feedback,
without introducing new components or assumptions.

--------------------------------------------------
COMPONENT INTERPRETATION RULE (CRITICAL)
--------------------------------------------------

The presence of an object_name ALWAYS implies that an object exists
and MUST be planned.

If components is empty or None:
- This indicates a SINGLE-COMPONENT (atomic) object
- It does NOT mean that no object exists
- You MUST still produce a design plan for the object described by object_name

--------------------------------------------------
OBJECT TYPE CONSTRAINT (CRITICAL)
--------------------------------------------------

If the object is a SIMPLE or ATOMIC object
(e.g., cube, cuboid, block, sphere, cylinder, rod):

- Treat the object as a SINGLE COMPONENT
- Do NOT decompose it into sub-parts
- Do NOT introduce bases, supports, platforms, walls, openings, roofs, or layers
- The plan should describe ONLY:
  - Overall shape
  - Uniformity
  - Approximate size
  - Whether it is solid or hollow
  - Static nature (if applicable)

Component decomposition is ONLY allowed when the intent
EXPLICITLY mentions multiple components or assemblies.

--------------------------------------------------
PLANNING OBJECTIVE
--------------------------------------------------

Produce a human-readable CAD design plan that:

- Uses a numbered list
- Mentions ONLY components present in the design intent
- Uses approximate or relative proportions
- Avoids all implementation details
- Reads like a design review note, not a technical specification

--------------------------------------------------
STRICT PROHIBITIONS
--------------------------------------------------

You MUST NOT:
- Write or imply OpenSCAD or CAD code
- Mention primitives (cube, cylinder, sphere, etc.)
- Mention coordinates, rotations, translations, or transforms
- Introduce components not present in the design intent
- Add functional features (doors, openings, mechanisms) unless stated
- Add aesthetic or cosmetic assumptions

--------------------------------------------------
STYLE EXAMPLES (FOLLOW THIS EXACTLY)
--------------------------------------------------

Example 1: Simple Multi-Component Object (Airplane)

Design Plan:
1. Fuselage: Rounded cylindrical body forming the main structure, with length approximately 100 units.
2. Wings: Centrally positioned wings with a slight backward sweep, total wingspan approximately 120 units.
3. Tail: Standard tail configuration consisting of horizontal stabilizers and a vertical fin at the rear,
   proportionally sized relative to the fuselage.

Approval Question:
Does this plan look good to proceed with CAD modeling?

---

Example 2: Simple Atomic Object (Cube)

Design Plan:
1. Single solid cubic body forming the entire object.
2. All faces are equal in size, defining a uniform cube.
3. Each edge has an approximate length of 50 units.
4. The object is static with no internal cavities or additional features.

Approval Question:
Does this plan look good to proceed with CAD modeling?

---

Example 3: Simple Elongated Object (Rod / Cylinder-like)

Design Plan:
1. Single elongated solid body forming the entire object.
2. Length is significantly greater than the cross-sectional thickness.
3. The object has uniform cross-section along its length.
4. No internal features or attachments are present.

Approval Question:
Does this plan look good to proceed with CAD modeling?

---

Example 4: Simple Multi-Part Object (Bracket)

Design Plan:
1. Main support body forming the structural core of the bracket.
2. Secondary mounting arm extending from the main body at a fixed angle.
3. Both components are proportionally sized to function as a single rigid unit.

Approval Question:
Does this plan look good to proceed with CAD modeling?

--------------------------------------------------
OUTPUT INSTRUCTIONS
--------------------------------------------------

Return values for the following fields ONLY:
- design_plan
- ready_for_review

Rules:
- design_plan MUST follow the numbered-list style shown above
- design_plan MUST end with a clear approval question
- ready_for_review MUST be true
- Do NOT include explanations outside these fields
- Ensure the plan is concise and focused on the object's structure and proportions
"""
