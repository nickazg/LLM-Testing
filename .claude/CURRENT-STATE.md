# Current State

## Project Direction
Automated LLM benchmarking framework comparing coding performance across CLI interfaces (Claude Code, Open Code, Kilo CLI) with 5 models (Qwen3 Coder 30B, MinimaxM2.7, GLM-5, Gemma 4 31B, Opus 4.6). Core experiment: measuring skill uplift delta per model.

## Current Phase
MVP implementation complete. All 19 tasks done. 44 tests passing. CLI entry point working.

## What's Built
- Python package `llm-bench` with `run` and `dashboard` subcommands
- 3 CLI adapters (Claude Code, Open Code, Kilo) with async subprocess execution
- Task loader with tier/ID filtering
- Workspace manager with skill injection and per-CLI context file writing
- Automated scorer (validate.py runner + efficiency metrics)
- LLM judge scorer (blind, rubric-based, via Claude Code)
- Result JSON persistence
- FastAPI dashboard with matrix, skill uplift, efficiency, and run history views
- 2 tier 1 test tasks (hello world, fizzbuzz)

## What's Next
- Set up .env files for Claude Code model routing
- Create tier 2-4 tasks (especially tier 3/4 pairs for skill uplift experiment)
- Create skills for niche domains (USD, Houdini)
- Run first real benchmarks
- Refine adapters based on real CLI behavior
