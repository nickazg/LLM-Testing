# Current State

## Project Direction
Automated LLM benchmarking framework comparing coding performance across CLI interfaces (Claude Code, Kilo CLI) with free/cheap models via OpenRouter. Core experiment: measuring skill uplift delta per model. Includes DSPy-powered skill compilation to automatically optimize skills for weaker models.

## Current Phase
Qwen3 Coder 30B full experiment complete. 259 benchmark results total. Capability threshold theory strengthened.

## What's Built
- Python package `llm-bench` with `run`, `dashboard`, `info`, and `compile-skill` subcommands
- 3 CLI adapters (Claude Code, Open Code, Kilo) with async subprocess execution
- 23 benchmark tasks across 4 tiers + 4 domain skills (with 7 total variants)
- Skill variant system: `domain:variant` format, VARIANTS.yaml, resolve_skill_path()
- DSPy skill compiler with proxy + live metrics, Pydantic SkillDocument schema
- Mock hou module (SOP + Solaris variants) for Houdini testing without license
- FastAPI dashboard with matrix, skill uplift (variant comparison), efficiency, and run history views
- 69 unit tests passing
- 259 benchmark result files

## Task Inventory (23 tasks, 4 skills with 7 variants)
- Tier 1 (2): hello-world, fizzbuzz
- Tier 2 (6): csv-pipeline, cli-tool, log-processor, makefile, usd-scene, houdini-sop
- Tier 3 (6): expression-parser, git-hook, houdini-solaris, lru-cache, service-generator, usd-shot-assembly
- Tier 4 (9): usd-shot-assembly (reference), usd-shot-assembly-hints, usd-shot-assembly-compiled (glm45), usd-shot-assembly-compiled-live (glm45), usd-shot-assembly-compiled-qwen3, houdini-solaris (reference), houdini-solaris-compiled-qwen3, expression-parser, lru-cache

## Skill Variants
### usd-composition (6 variants)
- `reference` (144 lines) — broad API reference, hurts weak models
- `task-hints` (40 lines) — manual narrow skill
- `compiled-glm45` (80 lines) — DSPy proxy metric for glm-4.5
- `compiled-live-glm45` (59 lines) — DSPy live metric for glm-4.5
- `compiled-qwen3-30b` (76 lines) — DSPy proxy metric for qwen3-30b

### houdini-solaris (2 variants)
- `SKILL` (160 lines) — full Solaris reference
- `compiled-qwen3-30b` (74 lines) — DSPy proxy metric for qwen3-30b

## Key Findings

### Benchmark V1 (160 runs, 2026-04-05)
1. Tier difficulty calibration: 92% → 78% → 42% → 25%
2. Broad skills HURT weaker models (glm-4.5: 0.8→0.2 with USD skill)
3. Capability threshold: skills only help models strong enough to synthesize from examples

### Skill Variant Experiment (18 runs, 2026-04-06)
1. Narrower skills reduce harm: reference -0.20 avg uplift, hints -0.13, DSPy variants -0.10
2. DSPy-live recovered CC performance for glm-4.5: 0.2→0.8
3. No single skill variant works across CLIs

### CLI Confound (investigated 2026-04-06)
1. Kilo LSP false positives: Pyright flags all pxr API calls
2. CC proxy swallows telemetry: OpenRouter models show empty raw_output/tokens
3. CC hooks bloat context: superpowers SessionStart injects thousands of words

### Qwen3 Coder 30B Experiment (16 runs, 2026-04-06)
**USD Shot Assembly — skill uplift by variant (CC):**
| Variant | Score | Delta from baseline |
|---------|-------|---------------------|
| No skill (tier3) | 1.0 | baseline |
| reference | 0.7 | -0.3 |
| task-hints | 0.9 | -0.1 |
| compiled-glm45 | 0.9 | -0.1 |
| compiled-live-glm45 | 0.1 | -0.9 |
| compiled-qwen3-30b | 0.0 | -1.0 |

**Key findings:**
1. **qwen3-30b is ABOVE capability threshold** — scores 1.0 without skill, all skills hurt
2. **Model-specific DSPy compilation was WORST** — proxy score 1.0 but real score 0.0
3. **Cross-model transfer > model-specific**: glm45-compiled (0.9) beat qwen3-compiled (0.0)
4. **Root cause**: model hallucinated `LockVariant()` instead of skill's `GetVariantEditContext()`
5. **Proxy metric is not predictive** — optimizes structure, not behavioral compliance
6. **Houdini Solaris**: 0/6 across all variants and CLIs — above qwen3-30b's difficulty ceiling
7. **Kilo**: 0.0 on all USD/Houdini tasks — CLI environment blocks qwen3-30b entirely

### Emerging Theory: Skill Harm Zones
- **Below threshold** (can't do task at all): skill adds noise, model hallucinates from examples → NET HARM
- **At threshold** (sometimes passes): narrow, task-specific skills can tip the balance → POTENTIAL UPLIFT
- **Above threshold** (reliably passes): skill competes with model's correct priors → NET HARM
- The "sweet spot" for skill uplift is a narrow band around the capability threshold

## What's Next
1. Run live-metric DSPy compilation (actual benchmark in the loop) for more reliable optimization
2. Find models AT the capability threshold for each task (the uplift sweet spot)
3. Investigate why Kilo is 0.0 on everything for qwen3-30b specifically
4. Run frontier model (Opus 4.6) as ceiling benchmark
5. Consider adaptive skill injection: only inject when model is predicted to be at threshold
