# Current State

## Project Direction
Automated LLM benchmarking framework measuring coding performance across CLI interfaces (Claude Code, Kilo), with a three-category skill taxonomy to isolate different types of skill uplift. Core experiment: does structured knowledge close the gap between budget and frontier models?

## Current Phase
Phase 3 benchmark complete. 1,607 results across 13 models, 2 CLIs, 68 tasks. Full analysis report written.

## What's Built
- Python package `llm-bench` with `run`, `dashboard`, `info`, `compile-skill` subcommands
- 3 CLI adapters (Claude Code, Open Code, Kilo) with async subprocess execution
- **68 benchmark tasks** across 4 tiers
- **Three-category skill taxonomy**: Novel Knowledge, Workflow/Process, Domain Context
- **Heavy/light intensity** variants per skill type
- **75 DSPy-compiled skill variants** (15 skills × 5 target models)
- Parallel benchmark orchestrator (`scripts/full_benchmark.py`) with checkpointing
- Z.ai direct on both CC and Kilo (via custom provider in ~/.config/kilo/kilo.jsonc)
- FastAPI dashboard with skill type/intensity filters and uplift-by-type breakdown
- 75 unit tests passing

## Phase 3 Key Findings (1,607 runs)

### Model Rankings
1. GLM-5: 87% (best budget model by far)
2. glm-4.5-air-free: 72% (best free option)
3. qwen3-30b: 67% (solid all-rounder)
4. devstral: 22% (but 67% without skills — catastrophic skill interference)
5. gemma-4-31b: 23% (timeout-dominated, knows answers but too slow)
6. Everything else: <12%

### Skill Taxonomy Findings
- Skills only help models above capability threshold (~65%+ baseline)
- Novel skills: marginal uplift for strong models on genuinely unknown APIs
- Workflow light > workflow heavy (concise reminders beat prescriptive recipes)
- Context heavy > context light (more detail = better compliance)
- DSPy compilation: negligible effect overall, occasionally helps on specific weak spots

### Critical Discoveries
- Devstral: 0% on ALL 136 skill-variant runs (fundamental context integration failure)
- Scores are binary (1.0 or 0.0) — no partial understanding
- Import errors dominate weak model failures (CLI integration, not coding capability)
- Kilo outperforms CC for most budget models (leaner protocol = less overhead)
- Online benchmarks don't predict CLI performance

## What's Next
1. Investigate devstral's context integration failure — is it the skill injection path or the model?
2. Extended timeout experiments for gemma-4-31b (600s+)
3. Multi-run statistical validation for top 3 models
4. Production skill recommendations based on type/intensity findings
