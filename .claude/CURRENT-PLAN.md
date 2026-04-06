# Plan: Skill Variants + DSPy Integration

## Status: PHASES 1-3 COMPLETE

All implementation tasks finished. 69/69 tests passing.

## Completed

- [x] **Phase 1: Skill Variant Support**
  - [x] 1.1 Rename SKILL.md → reference.md, create VARIANTS.yaml
  - [x] 1.2 Add resolve_skill_path() to runner.py
  - [x] 1.3 Add skill_domain/skill_variant properties to TaskConfig
  - [x] 1.4 Write skills/usd-composition/task-hints.md (40-line narrow skill)
  - [x] 1.5 Create tasks/tier4/usd-shot-assembly-hints/ task
  - [x] 1.6 Add resolve_skill_path tests (5 tests)
  - [x] 1.7 Fix info command skill discovery for variants

- [x] **Phase 2: Dashboard Variant Comparison**
  - [x] 2.1 Update renderUpliftView() — variant comparison matrix with color-coded deltas

- [x] **Phase 3: DSPy Skill Compiler**
  - [x] 3.1 Add [compile] optional dependencies to pyproject.toml
  - [x] 3.2 Create src/llm_bench/compiler.py (SkillDocument, DSPy signature, proxy/live metrics, compile_skill orchestrator)
  - [x] 3.3 Wire compile-skill subcommand into cli.py
  - [x] 3.5 Add compiler tests (10 tests)

## Remaining (Phase 4: Run & Validate)

- [ ] Run benchmark with task-hints variant to test hypothesis
- [ ] Run compile-skill with proxy metric
- [ ] Compare reference vs task-hints vs compiled

## Execution Notes
- Outlines deferred: constrained decoding requires local models; using Pydantic schema validation instead
- DSPy is optional dependency — zero impact on core benchmark path
- proxy_metric is heuristic (structure, conciseness, API coverage); live_metric actually runs benchmark
- BootstrapFewShot chosen over MIPROv2 for initial version (simpler, fewer examples needed)
- Compilation cache stored in skills/{domain}/.compile-cache/ (gitignored)
- Dashboard falls back to original single-variant view when only one variant exists
