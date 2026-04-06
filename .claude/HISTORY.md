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

## 2026-04-04 — First Real Benchmarks: 5 Cheap Models on Both CLIs
- Researched OpenRouter free/cheap models — found many have limitations (no tool calling, provider restrictions, max_tokens caps)
- Selected 5 models that work on both Claude Code and Kilo: qwen3-coder-free, glm-4.5-air-free, glm-4.7-flash, qwen3-next-80b-free, glm-5
- Ran tier 1 benchmarks (hello-world + fizzbuzz) across all 5 models × 2 CLIs = 20 runs
- Results: 19/20 pass (qwen3-next-80b-free fizzbuzz times out on Kilo)
- Updated models.yaml with free tier section and removed unavailable models (qwen3.6-plus was 404)
- Discovered: Claude Code proxy supports limited providers (Qwen, Z-AI, Llama); Kilo has provider routing restrictions
- Dashboard verified working with all results visible
- **Status:** Benchmarking infrastructure validated, ready for tier 2-4 tasks and skill uplift experiments

## 2026-04-05 — Real-World Benchmark Tasks & Skills
- Implemented 14 new tasks across tiers 2-4 (total: 16 tasks)
- Tier 2 (6): csv-pipeline, cli-tool, log-processor, makefile, usd-scene, houdini-sop
- Tier 3 (6): lru-cache, expression-parser, git-hook, service-generator, usd-shot-assembly, houdini-solaris
- Tier 4 (2): usd-shot-assembly + usd-composition skill, houdini-solaris + houdini-solaris skill
- Created 2 skills: usd-composition (USD Python API reference), houdini-solaris (Solaris LOP reference)
- Built mock `hou` module (SOP variant tracks API calls, Solaris variant returns real Usd.Stage)
- Fixed: log-processor task.yaml wrong schema, expression-parser nonlocal→global, cli-tool char count mismatch
- Removed accidental solution stub files from templates
- Verified: all 16 tasks load, validators return 0.0 for empty templates, tier 3/4 pairs identical, 54 tests pass
- **Status:** Full task suite ready for benchmarking

## 2026-04-05 — Full Benchmark: 160 Runs (5 models × 2 CLIs × 16 tasks)
- Ran complete end-to-end benchmark: 160 runs over 6.3 hours
- 2 of 5 models non-functional (qwen3-coder-free, qwen3-next-80b-free — all timeout)
- 3 GLM models produced real data: glm-4.5-air-free, glm-4.7-flash, glm-5
- Tier difficulty perfectly calibrated: T1=92%, T2=78%, T3=42%, T4=25% pass rates
- Best model: glm-5 on Claude Code (12/16 pass, avg=0.76)
- Hardest tasks: expression-parser, lru-cache, houdini-solaris (0/18 across all models)
- **Skill uplift headline: glm-5 + houdini-solaris skill went 0.00 -> 1.00 on Claude Code**
- **Surprise finding: USD composition skill HURT weaker models** (glm-4.5 dropped 0.80 -> 0.20)
- Root cause investigation: API hallucination amplification, context saturation, authority bias
- Key insight: skills only help models "on the cusp" — too-weak models get confused by extra context
- Implication: task-scoped skills safer than broad domain reference skills
- **Status:** First skill uplift data collected, findings inform skill design approach

## 2026-04-05 — Skill Variants + DSPy Compiler (Phases 1-3)
- Implemented skill variant system: `domain:variant` format, VARIANTS.yaml, resolve_skill_path()
- Created task-hints variant (40-line narrow skill vs 144-line reference)
- Built DSPy skill compiler with proxy/live metrics, BootstrapFewShot optimizer
- Added `compile-skill` subcommand to CLI
- Dashboard updated with variant comparison matrix in uplift view
- 69 tests passing
- **Status:** Implementation complete, ready for variant benchmarking

## 2026-04-06 — Skill Variant Experiment (Phase 4)
- Ran DSPy compilation: glm-5 as teacher → compiled-glm45 variant (80 lines, proxy score 0.80)
- Ran 12 benchmarks: 3 variants × 3 models × 2 CLIs on USD shot assembly
- **Results:** All skills net-negative on avg for weak models (reference -0.20, task-hints -0.13, compiled -0.10)
- **Highlight:** DSPy compiled skill got glm-4.5 Kilo from 0.1→0.8 (+0.7 uplift) — single biggest win
- **Surprise:** Same skill+model performs oppositely on different CLIs (CLI is a confound)
- **Confirmed:** glm-5 is immune to skill quality (always 1.0) — above capability threshold
- **Insight:** Model-specific optimization helps the target but may hurt other models
- **Status:** Variant experiment complete, 226 total results

## 2026-04-06 — CLI Confound Investigation + Live DSPy Compilation
- Investigated why same model+skill produces opposite results on CC vs Kilo
- **Root causes found:** Kilo LSP false positives (Pyright vs pxr), CC proxy swallows telemetry, CC hooks bloat context
- Fixed live metric bug: candidate skill wasn't being injected into run_single_task (added skill_path_override param)
- Ran DSPy live-metric compilation (34 min, 6 iterations, glm-5 teacher → glm-4.5 target on Kilo)
- Generated compiled-live-glm45 variant (59 lines, proxy score 1.00)
- Benchmarked all 5 variants × 3 models × 2 CLIs = 18 new runs
- **Key result:** DSPy-live variant recovered glm-4.5 on CC to 0.8 (from 0.2 with reference skill)
- **Key insight:** No single skill variant works across CLIs — CLI environment is the dominant variable
- **Status:** 238 total results, experiment complete
