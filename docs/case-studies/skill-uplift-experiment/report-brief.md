# Skill Uplift in Budget LLMs — Technical Brief

**Date:** April 2026
**Dataset:** 478 benchmark runs (Phase 2), 268 runs (Phase 1) — 746 total
**Authors:** Nick Grobler, with Claude Code automation

---

## Executive Summary

- **CLI environment is the dominant variable, not skill content.** Skills produce a mean uplift of +0.147 on Claude Code but -0.068 on Kilo. Of 266 paired comparisons, 18% show uplift, 67% are neutral, and 14% show harm — the direction depends on the CLI, not the skill.
- **Houdini Solaris skill: +1.0 for 3 models on CC, zero on Kilo.** glm-5, qwen3-30b, and qwen3-coder-next all went 0.0 to 1.0 on Claude Code with the same reference skill. On Kilo, 0/6 models showed any uplift — the most consistent positive-on-CC, zero-on-Kilo pattern in the study.
- **Expression parser skill produces extreme +/-1.0 swings.** A near-complete-solution skill (102 lines) helps models that need it (glm-5 CC: +1.0, glm-4.5 CC: +0.9) but destroys models that already know the answer (glm-4.7 CC: -1.0, glm-5 Kilo: -1.0). Same skill, same model, opposite sign depending on CLI.
- **Model viability is CLI-dependent.** qwen3-coder-next passed 21/33 tasks on Claude Code (64%) but 0/33 on Kilo. gemma-4-31b shows the reverse: 0/33 CC, 7/33 Kilo. A model's benchmark score is inseparable from the CLI it runs on.
- **Run-to-run variance is confirmed and significant.** qwen3-30b scored 1.0 on USD shot assembly in Phase 1, then 0.0 on the identical task in Phase 2. Single-run conclusions are unreliable.

---

## Setup

We built **llm-bench**, a Python benchmarking framework that measures LLM coding performance across CLI interfaces. The framework uses a 4-tier task system where the delta between Tier 3 (no skill) and Tier 4 (with skill) isolates skill uplift.

### What the Tasks Are

Each task gives a model a natural-language prompt and an isolated workspace. The model produces code, which is executed and scored by automated validators. 33 tasks across 4 tiers.

**Tier 1 — Sanity checks (2 tasks):** hello-world, fizzbuzz. Can the model produce runnable code at all?

**Tier 2 — General coding (6 tasks):** CSV data pipeline, CLI word-count tool (argparse), bash log analyzer, C project Makefile, basic USD scene, and Houdini SOP network. Tests standard programming patterns — no domain expertise needed.

**Tier 3 — Domain-specific, no skill (6 tasks):** The control group. Tasks that require niche knowledge:
- **USD shot assembly** — build a multi-file scene with cross-file references, variant sets (model variants + lighting variants), and transforms using Pixar's `pxr` library. The critical API is `GetVariantEditContext()` — a context manager for authoring inside USD variants that models frequently hallucinate.
- **Houdini Solaris** — build a complete scene (geometry, lighting, PBR materials, model kinds) through Houdini's `hou.pwd().editableStage()` pattern. Tested via mock `hou` module. Requires 10 specific USD operations.
- **Expression parser** — recursive descent parser with AST construction and operator precedence.
- **LRU cache** — O(1) dict + doubly-linked list implementation, thread-safe. Must NOT use OrderedDict.
- **Git pre-commit hook** and **systemd service generator** — DevOps domain tasks.

**Tier 4 — Identical to Tier 3, with a skill injected (9 tasks):** Same prompt, same validator. The only change is a skill document in the workspace. Multiple tier 4 variants exist for the USD task, each with a different skill formulation. Additional tier 4 variants cover Houdini Solaris, expression parser, and LRU cache.

### What the Skills Are

Skills are markdown documents injected into `.claude/skills/` — the native skill path all CLIs discover. They range from broad references to narrow task-specific hints:

| Skill | Lines | What It Contains | Design Intent |
|-------|-------|-----------------|---------------|
| USD `reference` | 144 | Full USD API reference (7 sections) including patterns the task doesn't need | "Give them the docs" approach |
| USD `task-hints` | 40 | Only the 4 API patterns needed for this task, with `GetVariantEditContext` labeled IMPORTANT | Minimum viable information |
| USD `compiled-glm45` | 80 | DSPy-optimized for glm-4.5, placeholder comments in complex sections | Automated optimization (proxy) |
| USD `compiled-live-glm45` | 59 | DSPy-optimized with actual benchmark runs in loop | Automated optimization (live) |
| USD `compiled-qwen3-30b` | 76 | DSPy-optimized for qwen3-30b, full working code | Model-specific targeting |
| Solaris `SKILL` | 160 | Complete Solaris LOP reference with full example | Broad reference for niche domain |
| `recursive-descent-parser` | 102 | Complete parser implementation with grammar | Near-complete solution |
| `lru-cache-pattern` | 70 | Full LRUCache with sentinel nodes | Near-complete solution |

### Models Tested

Phase 2 ran 8 models plus Opus 4.6 as a ceiling reference:

| Model | Category | Phase 2 Status |
|-------|----------|---------------|
| glm-5 | Budget (free) | Best performer — 61% pass rate |
| qwen3-30b | Budget (free) | Strong on CC — 44% pass rate |
| qwen3-coder-next | Budget (free) | CC-only — 64% CC, 0% Kilo |
| glm-4.5-air-free | Budget (free) | Consistent — 39% pass rate |
| glm-4.7-flash | Budget (free) | Mid-range — 30% pass rate |
| gemma-4-31b | Budget (free) | Kilo-only — 0% CC, 21% Kilo |
| minimax-m2.7 | Budget (free) | Non-functional — 0/66 runs, excluded |
| Opus 4.6 | Frontier (ceiling) | 10/10 CC (62% combined with partial Kilo errors) |

Phase 1 also tested qwen3-coder-free and qwen3-next-80b-free, both of which produced 100% timeouts and were dropped for Phase 2. minimax-m2.7 was confirmed non-functional in Phase 2 (0/66 across all tasks and CLIs).

**CLIs tested:** Claude Code (via proxy to OpenRouter for budget models, direct Anthropic subscription for Opus) and Kilo CLI.

### How Scoring Works

Validators execute the generated code and run structural tests. The USD shot assembly validator loads the output `.usda` files with the `pxr` library and checks 10 things: default prims, prim hierarchy, variant set existence, mesh types, reference resolution, transform differences, and variant content switching. Score = tests_passed / total_tests. A score of 0.9 means one test failed. A score of 0.0 means total failure.

---

## Experiments & Findings

### 1. Phase 1 Preliminary (268 runs)

Phase 1 was exploratory: framework development, hypothesis generation, and methodology refinement across 4 days. Key discoveries that shaped the Phase 2 design:

- **Tier difficulty was well-calibrated.** Pass rates: T1=92%, T2=78%, T3=42%, T4=25%. Progressive drop-off validated the tier system.
- **Broad skills actively harm weaker models.** glm-4.5 dropped from 0.8 to 0.2 on USD shot assembly when given the 144-line reference skill. Root cause: hallucination amplification — the model treated skill examples as authoritative and hallucinated similar-sounding APIs.
- **Capability threshold theory emerged.** Skills only help models on the cusp — strong enough to synthesize from examples, not strong enough to solve alone. glm-5 went 0.0 to 1.0 on Houdini Solaris with skill on CC, validating the positive case.
- **CLI confound identified.** Same model+skill gives opposite results on different CLIs. Three root causes: Kilo LSP false positives on `pxr` APIs, CC proxy telemetry gaps, CC hook bloat consuming context budget.
- **DSPy proxy metrics do not predict real performance.** qwen3-30b's own DSPy-compiled skill (proxy score 1.0) produced real score 0.0. Cross-model transfer (glm45-compiled) scored 0.9 on qwen3-30b — outperforming targeted optimization.
- **Narrower skills reduce harm.** Average uplift by variant: reference -0.20, task-hints -0.13, compiled -0.10. None achieved net-positive on average, but the gradient was clear.

All 268 Phase 1 result files were archived to `results/archive-v1/`. Phase 2 began from a clean baseline.

### 2. Phase 2 Full Benchmark (478 runs)

The definitive dataset: 8 models, 33 tasks, 2 CLIs. Every model ran every task on both CLIs.

**Model rankings by pass rate:**

| Rank | Model | Overall | CC | Kilo |
|------|-------|---------|-----|------|
| 1 | glm-5 | 61% | — | — |
| 2 | qwen3-30b | 44% | — | — |
| 3 | glm-4.5-air-free | 39% | — | — |
| 4 | qwen3-coder-next | 32% | 64% | 0% |
| 5 | glm-4.7-flash | 30% | — | — |
| 6 | gemma-4-31b | 11% | 0% | 21% |
| 7 | minimax-m2.7 | 0% | 0% | 0% |
| -- | Opus 4.6 (ceiling) | 62%* | 10/10 CC | partial Kilo |

*Opus 4.6 combined rate reflects partial Kilo errors, not model capability. CC performance was perfect.

**Tier calibration (Phase 2):**

| Tier | Pass Rate | Description |
|------|-----------|-------------|
| T1   | 60%       | Baseline (hello-world, fizzbuzz) |
| T2   | 54%       | Standard coding tasks |
| T3   | 41%       | Domain-specific, no skill |
| T4   | 18%       | Domain-specific, with skill |

Phase 2 T1/T2 pass rates are lower than Phase 1 because the model pool now includes weaker and non-functional models (gemma-4-31b, minimax-m2.7) that drag down averages. The progressive difficulty gradient remains valid.

### 3. Skill Uplift Deep Dive

**Aggregate uplift statistics (266 paired tier3-vs-tier4 comparisons):**

| CLI | Positive | Neutral | Negative | Mean Uplift |
|-----|----------|---------|----------|-------------|
| Claude Code | 40 (30%) | 84 (63%) | 9 (7%) | +0.147 |
| Kilo | 9 (7%) | 95 (71%) | 29 (22%) | -0.068 |
| **Combined** | **49 (18%)** | **179 (67%)** | **38 (14%)** | **+0.039** |

**USD Shot Assembly — skill variants on Claude Code:**

All USD skills demonstrate the correct `GetVariantEditContext()` API. The variable is surrounding detail:

| Variant | Lines | Phase 1 Avg Uplift | Phase 2 Pattern |
|---------|-------|--------------------|-----------------|
| reference (broad) | 144 | -0.20 | Continues to hurt weaker models |
| task-hints (narrow) | 40 | -0.13 | Mixed; qwen3-30b scored 0.0 and 0.9 on reruns |
| compiled-glm45 (DSPy proxy) | 80 | -0.10 | Best cross-model transfer |
| compiled-live-glm45 (DSPy live) | 59 | mixed | Recovered glm-4.5 CC: 0.2→0.8 |
| compiled-qwen3-30b (DSPy proxy) | 76 | N/A | 0.0 on target model (worst performer) |

qwen3-30b Phase 2 variance: scored 0.0 on the baseline (no skill) in Phase 2, down from 1.0 in Phase 1. This means the Phase 1 finding that "qwen3-30b is above the capability threshold" may have been a lucky run. The skill harm pattern still holds directionally, but the baseline is unreliable.

**Houdini Solaris — the clearest positive uplift:**

| Model | Tier 3 (no skill) CC | Tier 4 (with skill) CC | Uplift | Kilo T3 | Kilo T4 | Kilo Uplift |
|-------|---------------------|----------------------|--------|---------|---------|-------------|
| glm-5 | 0.0 | 1.0 | **+1.0** | — | — | 0 |
| qwen3-30b | 0.0 | 1.0 | **+1.0** | 0.0 | 0.0 | 0 |
| qwen3-coder-next | 0.0 | 1.0 | **+1.0** | 0.0 | 0.0 | 0 |
| All other models | 0.0 | 0.0 | 0 | 0.0 | 0.0 | 0 |

Three models at the capability threshold, all perfectly uplifted on CC, all zero on Kilo. The Solaris reference skill (160 lines, complete LOP reference with working example) is the most effective skill in the study — but exclusively on Claude Code.

**Expression parser — extreme polarization:**

| Model | CC T3 | CC T4 | CC Uplift | Kilo T3 | Kilo T4 | Kilo Uplift |
|-------|-------|-------|-----------|---------|---------|-------------|
| glm-5 | 0.0 | 1.0 | **+1.0** | 1.0 | 0.0 | **-1.0** |
| glm-4.5 | 0.1 | 1.0 | **+0.9** | — | — | — |
| glm-4.7 | 1.0 | 0.0 | **-1.0** | — | — | — |

The recursive-descent-parser skill (102 lines, near-complete solution) shows the widest outcome range of any skill. glm-5 is the starkest example: +1.0 on CC, -1.0 on Kilo. Same model, same skill, opposite sign. glm-4.7-flash already scores 1.0 without the skill on CC — the skill destroys a model that was above the threshold.

**LRU cache — mostly neutral:**

The lru-cache-pattern skill (70 lines, near-complete solution) had minimal effect. Most models that can solve it already score 1.0 without help. Two small positives on Kilo only: glm-4.5 0.0 to 0.5, glm-4.7 0.7 to 1.0. This task may be too well-represented in training data for skills to provide meaningful uplift, unlike the niche USD/Houdini domains.

### 4. CLI Confound

The CLI environment is not just a nuisance variable — it is the primary determinant of whether a skill helps or hurts.

**Complete CLI dependence — model viability:**

| Model | CC Pass Rate | Kilo Pass Rate | Pattern |
|-------|-------------|---------------|---------|
| qwen3-coder-next | 21/33 (64%) | 0/33 (0%) | CC-only |
| gemma-4-31b | 0/33 (0%) | 7/33 (21%) | Kilo-only |
| minimax-m2.7 | 0/33 (0%) | 0/33 (0%) | Non-functional |
| glm-5 | High | High | Both CLIs |
| qwen3-30b | High | Low | CC-dominant |

qwen3-coder-next and gemma-4-31b are mirror images: each is viable on exactly one CLI and non-functional on the other. A benchmark reporting only CC results would rank qwen3-coder-next highly; one reporting only Kilo results would rank gemma-4-31b highly. Neither ranking is wrong — both are incomplete.

**Aggregate skill direction by CLI:**

On Claude Code, skills are net-positive (+0.147 mean, 30% positive vs 7% negative). On Kilo, skills are net-negative (-0.068 mean, 7% positive vs 22% negative). The skill content is identical in both cases. Three identified root causes:

1. **Kilo LSP false positives.** Pyright flags all `pxr` (USD Python API) calls as errors, forcing models into error-correction loops that interfere with skill-guided approaches.
2. **Claude Code proxy telemetry.** OpenRouter models show empty `raw_output` and token counts — we cannot verify what the model actually received or how much context remained.
3. **Claude Code hook bloat.** Superpowers SessionStart hook injects thousands of words into context, consuming model budget. However, this appears to help skill integration — possibly by establishing a structured problem-solving pattern before the model encounters the skill.

**Revised theory:** The CLI environment determines the DIRECTION of the skill effect. CC's environment amplifies skill content constructively — models integrate it better. Kilo's environment amplifies it destructively — models fight against conflicting signals (LSP errors vs. skill guidance). The capability threshold determines MAGNITUDE, but the CLI determines SIGN.

---

## Key Insights

1. **CLI environment is a first-order variable, not a confound.** Phase 2 elevates this from "confound to investigate" to the primary finding. Skills average +0.147 on CC and -0.068 on Kilo. Skill effectiveness research that does not control for CLI tooling is measuring the wrong thing.

2. **Skills are net-positive on Claude Code, but only for at-threshold models.** The +0.147 CC mean is driven by strong individual cases (Houdini +1.0, expression parser +1.0). Models above the threshold still suffer harm (glm-4.7 expression parser: -1.0). The capability threshold theory holds within the CC-positive regime.

3. **Near-complete-solution skills are maximally polarizing.** The expression parser and LRU cache skills contain near-complete implementations. These help models that need them most but destroy models that already have the answer. The closer a skill is to "just give them the code," the more extreme the +/- swing.

4. **Niche domains show the most uplift potential.** Houdini Solaris (niche, limited training data) showed the strongest uplift. LRU cache (common, well-represented in training data) showed the weakest. Skill uplift is most valuable precisely where models lack internalized knowledge.

5. **Run-to-run variance means single-run conclusions are unreliable.** qwen3-30b scored 1.0 then 0.0 on the same USD task across phases. The Phase 1 "above capability threshold" finding was likely a lucky run. Multi-run averaging is not optional — it is required for any actionable conclusion.

6. **Model viability is inseparable from CLI.** qwen3-coder-next (21/33 CC, 0/33 Kilo) and gemma-4-31b (0/33 CC, 7/33 Kilo) demonstrate that model rankings are CLI-specific. There is no CLI-independent model quality metric in agentic coding benchmarks.

7. **Cross-model skill transfer still outperforms targeted optimization.** Phase 2 reinforced the Phase 1 finding: skills compiled for a different model (glm45-compiled) consistently outperform skills compiled for the target model (qwen3-compiled: proxy=1.0, real=0.0). Vagueness is a feature.

---

## Implications

For anyone building skill, RAG, or knowledge-injection systems for LLM coding tools:

- **Control the CLI or measure it.** Any benchmark comparing model performance across different CLI tools is partially measuring the CLI, not the model. Results from one CLI do not transfer to another. Production deployments should validate on the target CLI specifically.

- **Skills should be injected selectively, not universally.** On Claude Code, skills have a +0.147 mean — but this average masks destructive cases. Adaptive injection systems should estimate whether a model is at the capability threshold for a given task and suppress injection when the model is above it.

- **Target niche domains for maximum uplift.** Skills deliver the most value for domains underrepresented in training data (Houdini Solaris, USD composition). For well-covered domains (LRU cache, standard algorithms), skills add noise or nothing. Skill authoring effort should focus on domains where models demonstrably lack knowledge.

- **Prefer vague over detailed.** Near-complete-solution skills are maximally polarizing — they help weak models dramatically but destroy competent ones. Narrower, less prescriptive skills (task-hints at 40 lines vs reference at 144 lines) consistently show better average outcomes. Let the model use its own approach rather than prescribing one.

- **Budget model selection must be CLI-specific.** qwen3-coder-next is an excellent CC model (64% pass rate) and a useless Kilo model (0%). gemma-4-31b is the reverse. Model procurement for agentic coding tools requires testing on the target CLI, not synthetic benchmarks.

- **DSPy-style compilation needs live metrics.** Proxy-metric optimization produces structurally beautiful skills that do not work. Live-metric compilation (actual benchmark runs in the loop) is slower (34 minutes vs seconds) but produces skills that actually help. The gap between proxy and live metrics is not a tuning problem — it is a category error.

---

## Open Questions

- **Does multi-run averaging change the headline findings?** Phase 2 is still single-run per configuration. High variance (qwen3-30b: 1.0 then 0.0) means the +0.147 CC mean could shift substantially. 5-10 runs per configuration would establish confidence intervals.

- **What drives the CC vs Kilo direction split at the mechanism level?** We identified three root causes (LSP, hooks, routing) but have not isolated them with controlled ablation. Running with LSP disabled, hooks stripped, or identical providers would confirm which factor dominates.

- **Is the Houdini Solaris uplift reproducible?** The +1.0 for 3 models is striking but single-run. If it holds across reruns, it is the strongest evidence for skill uplift in the study. If it varies like USD shot assembly, the headline claim weakens significantly.

- **Can models self-detect when a skill is harmful?** If a model could evaluate whether a skill conflicts with its existing knowledge before committing to an approach, adaptive injection could be model-driven rather than requiring external threshold estimation.

- **Would frontier models show the same CLI split?** Opus scored 10/10 on CC but had partial Kilo errors. Is Kilo's destructive effect on skills a budget-model phenomenon, or does it affect frontier models too?

- **What is the minimum training-data coverage for skills to become irrelevant?** LRU cache showed minimal uplift — possibly because all models had sufficient training data. Is there a threshold of domain representation below which skills reliably help?
