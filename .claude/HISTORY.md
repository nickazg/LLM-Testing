# History

## 2026-04-03 — Design: LLM Testing Framework
- Brainstormed and validated full framework design through collaborative Q&A (12 questions)
- Defined: 4-tier task system, CLI adapters, scoring (automated + LLM-judge), skill uplift experiment
- Researched native skill mechanisms for Claude Code, Open Code, Kilo CLI — all share `.claude/skills/` discovery
- Researched CLI non-interactive modes and Python harness patterns
- Wrote design document: `docs/plans/2026-04-03-llm-testing-framework-design.md`

## 2026-04-03 — Implementation: MVP
- Implemented all 19 tasks from implementation plan
- Created Python package with src layout, pyproject.toml, hatchling build
- Built 3 CLI adapters (Claude Code w/ env file support, Open Code, Kilo) + registry
- Built task loader, workspace manager, automated scorer, LLM judge, result storage
- Built FastAPI dashboard with 4 views (matrix, skill uplift, efficiency scatter, run history)
- Created 2 tier 1 tasks (hello world, fizzbuzz) with validators
- 44 tests passing, CLI entry point working (`llm-bench run`, `llm-bench dashboard`)
- **Status:** MVP complete, ready for real benchmarks
