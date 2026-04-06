# Skill Uplift in Budget LLMs — Technical Brief

**Date:** April 2026
**Dataset:** 259 benchmark runs across 4 days
**Authors:** Nick Grobler, with Claude Code automation

---

## Executive Summary

- **Broad skills actively harm weaker models.** A 144-line USD API reference dropped glm-4.5 from 0.8 to 0.2 on the same task — hallucination amplification, not uplift.
- **The uplift sweet spot is a narrow capability band.** Skills only help models that are *on the cusp* — strong enough to synthesize from examples but not strong enough to solve the task alone. Too weak or too strong, and skills cause net harm.
- **Model-specific DSPy compilation was the worst performer.** A skill compiled specifically for qwen3-30b (proxy score 1.0) produced a real score of 0.0. A vaguer skill compiled for a *different* model scored 0.9. Cross-model transfer beat targeted optimization.
- **No single skill variant works across CLIs.** The same model+skill combination gives opposite results on Claude Code vs Kilo. CLI tooling (LSP, hooks, context injection) is a dominant confounding variable.
- **Proxy metrics do not predict real performance.** Structural quality (good markdown, code examples, API coverage) is orthogonal to whether a model will actually follow a skill's demonstrated patterns.

---

## Setup

We built **llm-bench**, a Python benchmarking framework that measures LLM coding performance across CLI interfaces. The framework uses a 4-tier task system where the delta between Tier 3 (no skill) and Tier 4 (with skill) isolates skill uplift.

### What the Tasks Are

Each task gives a model a natural-language prompt and an isolated workspace. The model produces code, which is executed and scored by automated validators.

**Tier 1 — Sanity checks (2 tasks):** hello-world, fizzbuzz. Can the model produce runnable code at all?

**Tier 2 — General coding (6 tasks):** CSV data pipeline, CLI word-count tool (argparse), bash log analyzer, C project Makefile, basic USD scene, and Houdini SOP network. Tests standard programming patterns — no domain expertise needed.

**Tier 3 — Domain-specific, no skill (6 tasks):** The control group. Tasks that require niche knowledge:
- **USD shot assembly** — build a multi-file scene with cross-file references, variant sets (model variants + lighting variants), and transforms using Pixar's `pxr` library. The critical API is `GetVariantEditContext()` — a context manager for authoring inside USD variants that models frequently hallucinate.
- **Houdini Solaris** — build a complete scene (geometry, lighting, PBR materials, model kinds) through Houdini's `hou.pwd().editableStage()` pattern. Tested via mock `hou` module. Requires 10 specific USD operations.
- **Expression parser** — recursive descent parser with AST construction and operator precedence.
- **LRU cache** — O(1) dict + doubly-linked list implementation, thread-safe. Must NOT use OrderedDict.
- **Git pre-commit hook** and **systemd service generator** — DevOps domain tasks.

**Tier 4 — Identical to Tier 3, with a skill injected (9 tasks):** Same prompt, same validator. The only change is a skill document in the workspace. Multiple tier 4 variants exist for the USD task, each with a different skill formulation.

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

The key experiment: all USD skills show the correct `GetVariantEditContext()` API. The variable is how much surrounding detail they include — which turned out to be the critical factor.

### How Scoring Works

Validators execute the generated code and run structural tests. The USD shot assembly validator loads the output `.usda` files with the `pxr` library and checks 10 things: default prims, prim hierarchy, variant set existence, mesh types, reference resolution, transform differences, and variant content switching. Score = tests_passed / 10. A score of 0.9 means one test failed (e.g., variant content missing). A score of 0.0 means total failure.

**Models tested:** glm-4.5-air-free, glm-4.7-flash, glm-5, qwen3-30b (2 Qwen free models excluded — 100% timeout).

**CLIs tested:** Claude Code (via proxy to OpenRouter) and Kilo CLI.

---

## Experiments & Findings

### 1. V1 Benchmark (160 runs, 6.3 hours)

**What we tested:** Full matrix of 5 models x 2 CLIs x 16 tasks to establish baselines and tier calibration.

| Tier | Pass Rate | Description |
|------|-----------|-------------|
| T1   | 92%       | Baseline (hello-world, fizzbuzz) |
| T2   | 78%       | Standard coding tasks |
| T3   | 42%       | Domain-specific, no skill |
| T4   | 25%       | Domain-specific, with skill |

- Tier difficulty was well-calibrated with progressive drop-off.
- 2 of 5 models (both Qwen free-tier) were non-functional — 100% timeout rate. Only the 3 GLM models produced usable data.
- **The headline finding:** glm-4.5 scored 0.8 on USD shot assembly *without* a skill, then dropped to 0.2 *with* the broad 144-line skill. The skill didn't help — it actively harmed the model through hallucination amplification. The model treated skill examples as authoritative and hallucinated similar-sounding APIs (e.g., `GetPrototypeStage`, `.edit()` instead of the correct `GetVariantEditContext`).
- **One clear positive:** glm-5 went 0.0 to 1.0 on Houdini Solaris with its skill on Claude Code. This model was exactly at the capability threshold.

### 2. Skill Variant Experiment (18 runs)

**What we tested:** Whether narrower, more focused skills reduce the harm seen in V1, including DSPy-compiled variants.

| Variant | Lines | Avg Uplift | Best Case |
|---------|-------|------------|-----------|
| reference (broad) | 144 | -0.20 | -- |
| task-hints (manual narrow) | 40 | -0.13 | -- |
| compiled-glm45 (DSPy proxy) | 80 | -0.10 | -- |
| compiled-live-glm45 (DSPy live) | 59 | mixed | glm-4.5 CC: 0.2 to 0.8 |

- Narrower skills reduce harm but none achieve net-positive uplift *on average*.
- DSPy live-metric compilation (34 minutes, actual benchmark runs in the optimization loop) recovered glm-4.5 performance on Claude Code from 0.2 back to 0.8.
- **Critical discovery:** The DSPy-compiled skill got glm-4.5 on Kilo from 0.1 to 0.8 (+0.7 uplift), but the same skill on Claude Code showed different behavior. Every variant that helps one CLI hurts or is neutral on the other.

### 3. CLI Confound Investigation

**What we tested:** Why the same model+skill gives opposite results on different CLIs.

Three root causes identified:

- **Kilo LSP false positives:** Pyright flags all `pxr` (USD Python API) calls as errors, forcing the model into error-correction loops that can accidentally help or hurt.
- **Claude Code proxy telemetry:** OpenRouter models show empty `raw_output` and token counts — we cannot verify what the model actually received.
- **Claude Code hook bloat:** Superpowers SessionStart hook injects thousands of words into context, consuming the model's budget for the actual task.

The benchmark measures the combined system of model + skill + CLI environment, not just model+skill. More realistic, but it complicates uplift isolation.

### 4. Qwen3-30b Deep Dive (16 runs)

**What we tested:** A model that's strong enough to pass USD tasks without help — does skill uplift still apply?

**USD Shot Assembly scores on Claude Code by variant:**

| Variant | Score | Delta |
|---------|-------|-------|
| No skill (baseline) | 1.0 | -- |
| reference | 0.7 | -0.3 |
| task-hints | 0.9 | -0.1 |
| compiled-glm45 | 0.9 | -0.1 |
| compiled-live-glm45 | 0.1 | -0.9 |
| compiled-qwen3-30b | 0.0 | -1.0 |

- qwen3-30b is **above** the capability threshold — it scores 1.0 without any skill. Every skill variant hurts it.
- **The skill detail paradox:** The vaguer glm45-compiled skill (with placeholder comments like `# configure mesh...`) scored 0.9. The detailed qwen3-compiled skill (full working code, proxy score 1.0) scored 0.0. More detailed skills push the model to attempt complex operations it then hallucinates. Vague skills let the model use its own correct approach.
- **Cross-model transfer wins:** A skill compiled for glm-4.5 outperformed a skill compiled specifically for qwen3-30b (0.9 vs 0.0).
- Kilo scored 0.0 on all 11 USD/Houdini runs for qwen3-30b — the CLI environment completely blocks this model on domain tasks.
- Houdini Solaris was 0/6 across all variants and CLIs — above qwen3-30b's difficulty ceiling entirely.
- **High run-to-run variance:** task-hints produced both 0.0 and 0.9 on the same configuration, indicating single-run conclusions are unreliable.

---

## Key Insights

1. **Skills are not universally helpful.** Default to no-skill unless you have evidence the model is at the capability threshold for the specific task. Injecting knowledge into a capable model is actively harmful.

2. **Less is more for skill content.** Narrow, task-specific hints (40 lines) consistently outperform broad API references (144 lines). When in doubt, be vaguer — let the model use its own approach rather than prescribing one.

3. **Proxy metrics for skill quality are misleading.** A skill can score perfectly on structural quality (good markdown, code examples, API coverage) and produce 0.0 real performance. The only reliable metric is running the actual benchmark.

4. **Cross-model skill transfer can outperform targeted optimization.** A skill compiled for a weaker model may work better on a stronger model, precisely because it's less prescriptive.

5. **CLI tooling is a first-order variable.** LSP feedback, context injection hooks, and provider routing affect results as much as skill content. Skill optimization may need to be CLI-specific, not just model-specific.

6. **The capability threshold is real and narrow.** Three zones exist: below (skill adds noise, net harm), at (narrow skills can help, potential uplift), above (skill competes with correct priors, net harm). The sweet spot is a thin band.

7. **Single-run benchmarks are insufficient.** High variance between identical runs means statistical significance requires multiple runs per configuration, which dramatically increases cost and time.

---

## Implications

For anyone building skill, RAG, or knowledge-injection systems for LLM coding tools:

- **Retrieval alone is not enough.** Serving correct documentation to a model does not guarantee it will follow it. Models hallucinate plausible alternatives even when the correct API is in context. Behavioral compliance is a separate problem from information availability.
- **Adaptive injection is the path forward.** Rather than always injecting skills, systems should estimate whether a model is at the capability threshold for a given task and only inject when uplift is likely. This requires a capability model per task-model pair.
- **Skill authoring guidelines need to change.** The instinct to write comprehensive, detailed skills is counterproductive. The best-performing skills were narrow, task-specific, and intentionally vague about implementation details.
- **CLI environment must be controlled or measured.** Any benchmark that compares model performance across different CLI tools is partially measuring the CLI, not just the model. Results are not portable across tooling without explicit confound measurement.
- **DSPy-style compilation is promising but needs live metrics.** Proxy-metric optimization produces structurally beautiful skills that don't work. Live-metric compilation (actual benchmark in the loop) is slower but produces skills that actually help.

---

## Open Questions

- **Where exactly is the threshold per model per task?** We identified zones but lack granular mapping. A systematic sweep with many models on a single task would answer this.
- **Does multi-run averaging change the conclusions?** High run-to-run variance means some findings may not hold. 5-10 runs per configuration would establish statistical reliability.
- **Would frontier models (Opus 4.6) show the same skill-harm pattern?** We tested only budget/mid-tier models. Frontier models may handle skills differently.
- **Can the model self-detect when a skill is harmful?** If a model could evaluate whether a skill is helpful before using it, adaptive injection could be model-driven rather than externally orchestrated.
- **Is the CLI confound reproducible?** Our investigation identified plausible root causes but didn't isolate them with controlled experiments. A CLI-controlled ablation study would confirm.

---

## Next Steps

1. **Multi-run reliability pass.** Rerun the key configurations 5x each to establish confidence intervals and verify headline findings.
2. **Frontier ceiling benchmark.** Run Opus 4.6 on the full task set to establish upper-bound performance and test whether skills harm frontier models.
3. **Adaptive skill injection prototype.** Build a threshold estimator that predicts per-model-task whether skill injection will help, and only injects when positive uplift is likely.
4. **CLI ablation study.** Run identical model+skill on both CLIs with LSP disabled, hooks stripped, and telemetry captured to isolate the CLI confound.
5. **Expand to more domains.** Current findings are heavily weighted toward USD/Houdini. Testing across more domains (web, systems, data) would validate generalizability.
