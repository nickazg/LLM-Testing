# Current State

## Project Direction
Automated LLM benchmarking framework comparing coding performance across CLI interfaces (Claude Code, Kilo CLI) with free/cheap models via OpenRouter. Core experiment: measuring skill uplift delta per model.

## Current Phase
Full benchmark complete. 160 runs across 5 models × 2 CLIs × 16 tasks. First skill uplift data collected.

## What's Built
- Python package `llm-bench` with `run`, `dashboard`, and `info` subcommands
- 3 CLI adapters (Claude Code, Open Code, Kilo) with async subprocess execution
- 16 benchmark tasks across 4 tiers + 2 domain skills
- Mock hou module (SOP + Solaris variants) for Houdini testing without license
- FastAPI dashboard with matrix, skill uplift, efficiency, and run history views
- 54 unit tests passing
- 170 benchmark result files

## Task Inventory (16 tasks, 2 skills)
- Tier 1 (2): hello-world, fizzbuzz
- Tier 2 (6): csv-pipeline, cli-tool, log-processor, makefile, usd-scene, houdini-sop
- Tier 3 (6): expression-parser, git-hook, houdini-solaris, lru-cache, service-generator, usd-shot-assembly
- Tier 4 (2): usd-shot-assembly+skill, houdini-solaris+skill

## Benchmark Results (160 runs, 6.3h)

### Tier Pass Rates (GLM models only)
| Tier | Avg Score | Pass Rate |
|------|-----------|-----------|
| 1 | 0.92 | 92% |
| 2 | 0.83 | 78% |
| 3 | 0.41 | 42% |
| 4 | 0.30 | 25% |

### Model Rankings
| Model | CLI | Pass | Avg |
|-------|-----|------|-----|
| glm-5 | Claude Code | 12/16 | 0.76 |
| glm-5 | Kilo | 11/16 | 0.69 |
| glm-4.5-air-free | Claude Code | 11/16 | 0.68 |
| glm-4.7-flash | Kilo | 9/16 | 0.61 |
| glm-4.5-air-free | Kilo | 8/16 | 0.53 |
| glm-4.7-flash | Claude Code | 6/16 | 0.45 |

### Skill Uplift Findings
- **glm-5 + houdini-solaris skill + CC: 0.00 -> 1.00 (+1.00)** — massive uplift
- USD composition skill HURT weaker models (glm-4.5: -0.60, glm-4.7: -0.40)
- Root cause: API hallucination amplification, context saturation, authority bias
- Skills only help models "on the cusp" — strong enough to leverage reference but weak enough to need it

### Non-Functional Models
- qwen3-coder-free: 0/32 (all timeout on both CLIs)
- qwen3-next-80b-free: 0/32 (all timeout on both CLIs)

## Key Learnings
1. Tier difficulty calibration works perfectly (92% -> 78% -> 42% -> 25%)
2. Domain-specific tasks (USD, Houdini) are genuinely hard for budget models
3. expression-parser, lru-cache, houdini-solaris: 0/18 across all models — good uplift baselines
4. Skills can actively harm models below a capability threshold
5. Task-scoped skills > domain-scoped skills for weaker models
6. Kilo and Claude Code show different model strengths (glm-4.7 better on Kilo, glm-4.5 better on CC)

## What's Next
- Run frontier model (Opus 4.6) as ceiling benchmark
- Design narrower, task-scoped skills to test if they help weaker models
- Add more tier 3/4 pairs for expression-parser and lru-cache
- Investigate Open Code adapter
- Consider removing the 2 non-functional Qwen models from default runs
