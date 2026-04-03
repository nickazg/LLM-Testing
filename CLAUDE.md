# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

LLM-Testing — an automated benchmarking framework that measures LLM coding performance across CLI interfaces (Claude Code, Open Code, Kilo CLI), with a focus on quantifying **skill uplift**: how much structured knowledge closes the gap between budget models (Qwen3 Coder 30B, Gemma 4 31B) and frontier models (Opus 4.6).

## Tech Stack

- **Python 3.11+** — test harness, scoring, data processing
- **FastAPI + Chart.js** — lightweight self-contained dashboard (no build step, no node_modules)
- **hatchling** — build backend

## Build & Run

```bash
# Install
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run a single test
pytest tests/test_models.py::test_task_config_from_yaml -v

# Run benchmarks
llm-bench run --models opus,qwen3-30b --clis claude-code,kilo --tiers 1

# Launch dashboard
llm-bench dashboard --port 8080
```

## Architecture

- `src/llm_bench/` — Python package (src layout)
  - `cli.py` — argparse CLI entry point (`llm-bench` command)
  - `runner.py` — async orchestrator: task x CLI x model matrix execution
  - `adapters/` — CLI-specific adapters (claude_code.py, open_code.py, kilo.py) + registry
  - `workspace.py` — temp dir setup, template copying, skill injection, context file writing
  - `scoring.py` — automated validation (runs validate.py) + efficiency metrics
  - `judge.py` — LLM-as-judge via Claude Code (blind scoring, rubric-based)
  - `models.py` — dataclasses: TaskConfig, RunResult, Scores, EfficiencyMetrics
  - `results.py` — JSON result persistence
  - `dashboard/app.py` — FastAPI server + inline HTML/JS dashboard
- `tasks/tier{1-4}/` — self-contained task directories (task.yaml, template/, validate.py)
- `skills/` — skill source files (copied into .claude/skills/ at runtime)
- `results/` — JSON output per run (gitignored)

## Key Design Decisions

- Skills injected via `.claude/skills/<name>/SKILL.md` — the only path all three CLIs share natively
- Claude Code uses CLAUDE.md, Open Code and Kilo use AGENTS.md — adapters write the correct file per CLI
- Claude Code model selection via `.env` file swapping (user maintains separate .env files per model)
- Tier 3/4 task pairing is the core experiment: identical tasks, one variable changed (skill present or not)
- LLM judge is blind — doesn't know which model/CLI produced the code
- Run and score phases are independent — raw outputs stored separately, re-scorable without re-running
