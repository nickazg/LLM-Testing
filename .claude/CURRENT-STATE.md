# Current State

## Project Direction
Automated LLM benchmarking framework comparing coding performance across CLI interfaces (Claude Code, Kilo CLI) with free/cheap models via OpenRouter. Core experiment: measuring skill uplift delta per model. Includes DSPy-powered skill compilation to automatically optimize skills for weaker models.

## Current Phase
Full skill variant experiment complete. 238 benchmark results. CLI confound identified and investigated.

## What's Built
- Python package `llm-bench` with `run`, `dashboard`, `info`, and `compile-skill` subcommands
- 3 CLI adapters (Claude Code, Open Code, Kilo) with async subprocess execution
- 19 benchmark tasks across 4 tiers + 2 domain skills (+ 5 variant tasks)
- Skill variant system: `domain:variant` format, VARIANTS.yaml, resolve_skill_path()
- DSPy skill compiler with proxy + live metrics, Pydantic SkillDocument schema (live metric bug fixed)
- Mock hou module (SOP + Solaris variants) for Houdini testing without license
- FastAPI dashboard with matrix, skill uplift (variant comparison), efficiency, and run history views
- 69 unit tests passing
- 238 benchmark result files

## Task Inventory (19 tasks, 2 skills with 4 variants)
- Tier 1 (2): hello-world, fizzbuzz
- Tier 2 (6): csv-pipeline, cli-tool, log-processor, makefile, usd-scene, houdini-sop
- Tier 3 (6): expression-parser, git-hook, houdini-solaris, lru-cache, service-generator, usd-shot-assembly
- Tier 4 (5): usd-shot-assembly (reference), usd-shot-assembly-hints (task-hints), usd-shot-assembly-compiled (DSPy proxy), usd-shot-assembly-compiled-live (DSPy live), houdini-solaris

## Skill Variants (usd-composition)
- `reference` (144 lines) — broad API reference, hurts weak models
- `task-hints` (40 lines) — manual narrow skill, less harmful but not helpful
- `compiled-glm45` (80 lines) — DSPy proxy metric, high variance
- `compiled-live-glm45` (59 lines) — DSPy live metric, best overall for target model on CC

## Key Findings

### Benchmark V1 (160 runs, 2026-04-05)
1. Tier difficulty calibration: 92% → 78% → 42% → 25%
2. Broad skills HURT weaker models (glm-4.5: 0.8→0.2 with USD skill)
3. Capability threshold: skills only help models strong enough to synthesize from examples

### Skill Variant Experiment (18 runs, 2026-04-06)
1. **Narrower skills reduce harm**: reference -0.20 avg uplift, hints -0.13, DSPy-proxy -0.10, DSPy-live -0.10
2. **DSPy-live recovered CC performance**: glm-4.5 CC went 0.2→0.8 (matching no-skill baseline)
3. **DSPy-proxy had best single uplift**: glm-4.5 Kilo 0.1→0.8 (+0.7)
4. **No skill works across CLIs**: every variant that helps one CLI hurts or is neutral on the other

### CLI Confound (investigated 2026-04-06)
1. **Kilo LSP false positives**: Pyright flags all pxr API calls — can destroy or save model through forced iteration
2. **CC proxy swallows telemetry**: OpenRouter models via proxy show empty raw_output/tokens
3. **CC hooks bloat context**: superpowers SessionStart injects thousands of words, consuming context budget
4. **Result**: benchmark partially measures CLI tooling behavior, not just model capability

## What's Next
1. Consider CLI-specific skill routing (different variant per CLI)
2. Investigate reducing CC hook injection for non-Anthropic models
3. Add more tier 3/4 pairs for expression-parser and lru-cache
4. Run frontier model (Opus 4.6) as ceiling benchmark
5. Consider normalizing for CLI confound in scoring/dashboard
