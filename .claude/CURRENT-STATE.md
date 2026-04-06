# Current State

## Project Direction
Automated LLM benchmarking framework comparing coding performance across CLI interfaces (Claude Code, Kilo CLI) with free/cheap models via OpenRouter. Core experiment: measuring skill uplift delta per model. Phase 2 clean benchmark complete with definitive dataset.

## Current Phase
Phase 2 complete. 478 clean benchmark results. CLI environment confirmed as dominant variable for skill effectiveness.

## What's Built
- Python package `llm-bench` with `run`, `dashboard`, `info`, and `compile-skill` subcommands
- 3 CLI adapters (Claude Code, Open Code, Kilo) with async subprocess execution
- 33 benchmark tasks across 4 tiers + 4 domain skills (with 15+ variants)
- Skill variant system: `domain:variant` format, VARIANTS.yaml, resolve_skill_path()
- DSPy skill compiler with proxy + live metrics, model-specific compilation for 7 models
- Mock hou module (SOP + Solaris variants) for Houdini testing without license
- FastAPI dashboard with matrix, skill uplift, efficiency, and run history views
- Case study skill with structured logging and report generation
- 69 unit tests passing
- 478 Phase 2 results + 268 archived Phase 1 results = 746 total

## Key Findings — Phase 2 (Definitive)

### Headline: CLI Environment Determines Skill Effect Direction
- 266 paired tier3-vs-tier4 comparisons
- **Claude Code: mean uplift +0.147** (40 positive, 84 neutral, 9 negative)
- **Kilo: mean uplift -0.068** (9 positive, 95 neutral, 29 negative)
- Same skill, same model, opposite outcome depending on CLI

### Model Rankings (Phase 2, 478 runs)
| Model | Pass Rate | CC | Kilo |
|-------|-----------|-----|------|
| opus4.6 (ceiling) | 62% | 10/10 | 0/6 (OpenRouter error) |
| glm-5 | 61% | 25/33 | 15/33 |
| qwen3-30b | 44% | 18/33 | 11/33 |
| glm-4.5-air-free | 39% | 13/33 | 13/33 |
| qwen3-coder-next | 32% | 21/33 | **0/33** |
| glm-4.7-flash | 30% | 9/33 | 11/33 |
| gemma-4-31b | 11% | **0/33** | 7/33 |
| minimax-m2.7 | 0% | 0/33 | 0/33 (dead) |

### Skill Uplift Highlights
- **Houdini Solaris**: +1.0 for glm-5, qwen3-30b, qwen3-coder-next on CC; 0 on Kilo
- **Expression parser**: ±1.0 extreme swings (helps or destroys depending on model+CLI)
- **USD shot assembly**: highly variable, best on CC with live-compiled variants
- **LRU cache**: mostly neutral — well-known domain, skills don't add much

### Confirmed Findings
1. **CLI is the dominant variable** — not skill content, not model capability
2. **Capability threshold still real** — skills help "at threshold" models, neutral/harmful otherwise
3. **High run-to-run variance** — qwen3-30b scored 1.0 (Phase 1) then 0.0 (Phase 2) on same task
4. **Model-CLI coupling is asymmetric** — qwen3-coder-next: 64% CC / 0% Kilo; gemma-4-31b: 0% CC / 21% Kilo

## What's Next
1. Multi-run statistical validation (5x per key configuration)
2. Investigate WHY CC amplifies skills constructively vs Kilo destructively
3. Adaptive skill injection prototype (inject only when uplift is predicted)
4. Expand to more domains beyond USD/Houdini
5. CLI-controlled ablation study (disable LSP, strip hooks)
