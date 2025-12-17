# CAD Generation Agent (Agentic Workflow)

This project implements an **agentic CAD generation pipeline** inspired by recent research on human-in-the-loop CAD workflows.

## Current Status
✅ Step-1: Design Intention Clarification & Parsing (COMPLETE)

## Architecture
- LangGraph-based agent workflow
- Human-in-the-loop clarification
- Structured design intent parsing
- LangSmith-based evaluation

## Project Structure

Nice 👍 — that’s a **big milestone**. I’ll treat this as: *“I’ve pushed the repo, what next / is this correct?”*

I can’t browse the repo contents live unless you ask me to review a specific file, but based on everything we built, here’s how to **lock this down properly** and make the repo “clean + professional”.

---

## ✅ What you’ve done correctly already

From our work, your repo now has:

* ✅ **Notebook-first development** (source of truth)
* ✅ **Deployable LangGraph workflow**
* ✅ **Clear Step-1 boundary (Design Intention + Parsing)**
* ✅ **LangGraph Studio support**
* ✅ **LangSmith evaluation pipeline**
* ✅ **Proper agentic architecture (not scripts)**

This is already *stronger than most GitHub agent repos*.

---

## 🔒 MUST-DO checklist (do these now)

### 1️⃣ `.gitignore` (very important)

Make sure you are **NOT committing secrets or noise**.

Your `.gitignore` should include at least:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv/
venv/

# Jupyter
.ipynb_checkpoints/

# LangSmith / LangGraph
.langgraph/
.langsmith/

# OS
.DS_Store
Thumbs.db
```

⚠️ **Confirm `.env` is NOT pushed**
(You pasted API keys earlier — rotate them if they were ever committed.)

---

### 2️⃣ `README.md` (minimum professional version)

At minimum, add this structure (you can refine later):

```md
# CAD Generation Agent (Agentic Workflow)

This project implements an **agentic CAD generation pipeline** inspired by recent research on human-in-the-loop CAD workflows.

## Current Status
✅ Step-1: Design Intention Clarification & Parsing (COMPLETE)

## Architecture
- LangGraph-based agent workflow
- Human-in-the-loop clarification
- Structured design intent parsing
- LangSmith-based evaluation

## Roadmap

* [ ] Step-2: Constraint Parser
* [ ] Step-3: CAD Geometry Planning
* [ ] Step-4: OpenSCAD / CAD Code Generation
* [ ] Step-5: Geometry Verification