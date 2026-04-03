# LLM Testing Framework — Design Document

## Purpose

An automated benchmarking framework that measures how well coding LLMs perform across CLI interfaces, with a focus on quantifying **skill uplift** — how much structured knowledge (skills) closes the gap between budget and frontier models.

## Test Matrix

**Models:** Qwen3 Coder 30B, MinimaxM2.7, GLM-5, Gemma 4 31B, Opus 4.6
**CLIs:** Claude Code, Open Code, Kilo CLI
**Tiers:**
- Tier 1: Single-file, well-known domain (e.g. "write a Python function to parse CSV")
- Tier 2: Multi-file, common patterns (e.g. "build a REST endpoint with tests")
- Tier 3: Domain-specific, no skill (e.g. "write a USD stage composition script")
- Tier 4: Identical to tier 3, but with a skill injected — the only variable changed

**Scoring dimensions:** correctness, completion, efficiency, quality, instruction following

## Repository Structure

```
LLM-Testing/
├── tasks/                  # Test task definitions
│   ├── tier1/
│   ├── tier2/
│   ├── tier3/
│   └── tier4/              # Mirrors tier3 — same tasks, skill enabled
├── skills/                 # Skill source files (copied into .claude/skills/ at runtime)
├── harness/                # Python test harness (core)
│   ├── adapters/           # CLI-specific adapters
│   │   ├── claude_code.py
│   │   ├── open_code.py
│   │   └── kilo.py
│   ├── scoring/            # Automated + LLM-judge scoring
│   └── runner.py           # Orchestration entry point
├── results/                # Raw run output (JSON per run)
├── dashboard/              # Lightweight web UI (self-contained)
│   ├── index.html          # Single-page app, no build step
│   └── app.py              # Python server, reads from results/
├── config/                 # CLI configs, model routing, environment setup
└── docs/
    └── plans/
```

## Task Definition Format

Each task is a self-contained directory:

```
tasks/tier2/rest-api-endpoint/
├── task.yaml              # Metadata, prompt, scoring config
├── template/              # Starting state — copied to temp dir before run
├── validate.py            # Automated validation (exit 0 = pass, JSON to stdout)
└── expected/              # Optional — expected output for diff checks
```

**task.yaml:**
```yaml
id: tier2-rest-api
name: "Build a REST endpoint with tests"
tier: 2
prompt: "Add a GET /users endpoint that returns JSON. Include pytest tests."
timeout: 300
skill: null                # tier4 tasks reference a skill ID here
tags: [python, api, testing]
scoring:
  automated:
    - correctness
    - completion
    - efficiency
  flagged:
    - quality
    - instruction_following
```

Tier 4 tasks are identical to their tier 3 counterpart except `skill` points to a skill in `skills/`. This keeps the comparison clean — one variable changed.

## Test Harness

Invocation:
```
python -m harness run --models qwen3-30b,opus4.6 --clis claude-code,kilo --tiers 1,2,3,4
```

**Run flow per test:**

1. Copy `template/` to a temp directory
2. Write the appropriate context file (CLAUDE.md for Claude Code, AGENTS.md for Open Code / Kilo)
3. If tier 4, copy the skill into `.claude/skills/<skill-name>/SKILL.md` in the temp dir
4. For Claude Code, swap in the correct `.env` file for the target model
5. Launch the CLI via the adapter with the task prompt
6. Capture: stdout/stderr, wall time, token usage (where available)
7. Run `validate.py` against the final temp dir state
8. For flagged dimensions, run an LLM-judge pass
9. Write result JSON to `results/`
10. Clean up temp dir

### CLI Adapters

Each CLI has a thin adapter that normalizes:
- Launching the CLI in non-interactive mode
- Passing the task prompt
- Configuring which model to use (including .env swapping for Claude Code)
- Injecting skills via `.claude/skills/` (native to all three CLIs)
- Writing the correct project context file (CLAUDE.md vs AGENTS.md)
- Extracting token/cost metadata from output

### Context File Strategy

- **Claude Code** reads `CLAUDE.md`
- **Open Code** reads `AGENTS.md` (falls back to `CLAUDE.md`)
- **Kilo CLI** reads `AGENTS.md`

The adapter writes the appropriate file into the temp dir before launch.

### Skill Injection

All three CLIs natively discover skills at `.claude/skills/<name>/SKILL.md`. The harness copies the referenced skill into this path in the temp dir. No special configuration needed.

## Scoring System

### Automated (immediate)

- **Correctness** — `validate.py` exit code + test pass rate. Binary or fractional (3/5 tests = 0.6)
- **Completion** — expected files/state exist. Binary or fractional.
- **Efficiency** — token count, tool calls, wall time, cost. Raw metrics captured during run.

### LLM-Judge (batch post-step)

- **Quality** — code reviewed against a rubric (idiomatic patterns, readability, no unnecessary complexity). Score 1-5 + reasoning.
- **Instruction Following** — did it do exactly what was asked? Score 1-5 + reasoning.

The judge is **Claude Code invoked with Opus** (using the user's subscription). It receives the original prompt, task.yaml criteria, and the final code. It does NOT receive which model or CLI produced it — **blind judging** to avoid bias.

Any score below 3 or flagged as low-confidence by the judge is tagged for manual review.

### Aggregation

- Each dimension normalizes to 0-1
- Efficiency inverts (lower = better)
- Composite score optional — all dimensions remain individually visible

## Result Format

```json
{
  "task_id": "tier3-usd-stage",
  "model": "qwen3-30b",
  "cli": "claude-code",
  "skill": null,
  "scores": {
    "correctness": 1,
    "completion": 1,
    "efficiency": {"tokens": 4200, "tool_calls": 8, "wall_time_s": 45},
    "quality": {"score": null, "flagged": true},
    "instruction_following": {"score": null, "flagged": true}
  },
  "timestamp": "2026-04-03T14:30:00Z"
}
```

## Dashboard

Self-contained. No framework, no build pipeline.

**Tech:** `app.py` serves static files + reads result JSONs. `index.html` with Chart.js or Plotly.js inline.

**Views:**
- **Matrix** — models (rows) x CLIs (columns), cells show per-dimension scores. Filterable by tier.
- **Skill uplift** — tier 3 vs tier 4 side-by-side per model. The delta is the core insight.
- **Efficiency scatter** — tokens/time vs correctness per model.
- **Run history** — drill into any run, view full result JSON.
- **Manual review queue** — flagged items, score inline, saves back to result JSON.

## The Core Experiment: Skill Uplift

For every tier 3 task, a tier 4 twin exists — identical in every way except a skill is injected.

```
uplift = tier4_score - tier3_score
```

**Hypothesis:**
- Frontier models (Opus 4.6) show moderate uplift — they already know a lot
- Budget models (Qwen3 30B) show large uplift — skills compensate for thinner training data
- If budget + skill approaches frontier without skill, that's the key finding

## Environment & Model Routing

Claude Code uses `.env` file swapping to select models. The user maintains separate `.env` files per model. The harness adapter swaps the appropriate file before each run.

Open Code and Kilo CLI model selection handled through their respective config mechanisms (`opencode.json`, `kilo.jsonc`).
