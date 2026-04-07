# Current State

## Project Direction
Automated LLM benchmarking framework comparing coding performance across CLI interfaces (Claude Code, Kilo CLI) with free/cheap models via OpenRouter. Core experiment: measuring skill uplift delta per model, now with a three-category skill taxonomy to isolate different types of uplift.

## Current Phase
Skill taxonomy expansion complete. 68 tasks across 3 skill categories (novel/workflow/context) x 2 intensities (heavy/light). Ready for benchmark runs with new matrix.

## What's Built
- Python package `llm-bench` with `run`, `dashboard`, `info`, and `compile-skill` subcommands
- 3 CLI adapters (Claude Code, Open Code, Kilo) with async subprocess execution
- **68 benchmark tasks** across 4 tiers (was 33):
  - 23 baselines (T1-T3): 2 trivial, 6 multi-file, 15 domain-specific
  - 45 skill variants (T4): classified by type and intensity
- **Skill taxonomy** with 3 categories:
  - **Novel Knowledge** — genuinely new info (VFX APIs: USD, Houdini Solaris, PDG)
  - **Workflow/Process** — structured guidance on known tech (LRU cache, expression parser)
  - **Domain Context** — org-specific conventions on known tech (git hooks, systemd services)
- Each category has **heavy** (full reference/recipe) and **light** (guardrails/key patterns) intensity variants
- New task.yaml fields: `difficulty`, `skill_type`, `skill_intensity`, `skill_pair`
- CLI filtering: `--skill-types novel,workflow` and `--difficulties 1,2,3`
- Dashboard: skill type/intensity filters, uplift-by-type breakdown table
- 26 skills total (was 4): 18 novel (heavy+light for 9 VFX tasks), 4 workflow, 4 context
- DSPy skill compiler with proxy + live metrics (15+ compiled variants carry over)
- 75 unit tests passing
- 478 Phase 2 results + 268 archived Phase 1 results = 746 total

## Skill Taxonomy
| Category | What it measures | Tasks |
|----------|-----------------|-------|
| Novel Knowledge | Can the model learn from genuinely new API info? | 11 VFX tasks (USD render/skel/layers/shaders/metadata, Houdini solaris/PDG/instancing/render/lighting) |
| Workflow/Process | Does structured guidance improve execution of known tasks? | 2 tasks (LRU cache, expression parser) |
| Domain Context | Can the model apply org-specific rules it couldn't know? | 2 tasks (git hooks, systemd services) |

Model-relative category shift tracked as secondary dimension (same skill = Novel for budget models, Workflow for frontier).

## Key Findings — Phase 2 (Pre-taxonomy)
- CLI Environment determines skill effect direction (CC positive, Kilo negative)
- Capability threshold theory confirmed
- Previous findings remain valid but were conflating different uplift types

## What's Next
1. Run new taxonomy benchmark matrix to isolate uplift per skill type
2. Compare light vs heavy intensity — does the uplift come from alignment or being given the answer?
3. Multi-run statistical validation (5x per key configuration)
4. Investigate Novel vs Workflow vs Context uplift curves per model capability level
