# Skill Uplift in Budget LLMs: When Structured Knowledge Helps, Hurts, and Destroys Coding Performance

**Authors:** Nick Grobler  
**Date:** April 2026  
**Framework:** llm-bench v0.1  
**Total runs:** 259 across 4 experiments  

---

## Abstract

Can structured domain knowledge ("skills") close the coding performance gap between budget and frontier large language models? We present a controlled benchmarking study using a purpose-built framework (llm-bench) that measures skill uplift across 23 tasks, 6 models, and 2 CLI environments. Contrary to the intuitive hypothesis that skills should help weaker models most, we find that skills produce net harm in the majority of configurations. Performance degradation follows a capability threshold pattern: models below the threshold hallucinate from skill examples, models above it have their correct priors overridden. Only models near the threshold --- capable enough to synthesize from examples but not capable enough to solve unaided --- benefit. Furthermore, the CLI environment acts as a dominant confounding variable, with identical model-skill pairs producing opposite results across different interfaces. These findings suggest that blindly injecting domain knowledge into LLM coding workflows is counterproductive and that skill effectiveness depends on a narrow, model-specific capability band.

---

## 1. Introduction

The rapid proliferation of LLM-powered coding assistants has created a practical question for organizations with budget constraints: can structured domain knowledge compensate for using smaller, cheaper models instead of frontier systems? If a 30-billion-parameter model armed with the right reference material could match a frontier model's output on domain-specific tasks, the cost implications would be significant.

This paper investigates the **skill uplift hypothesis**: that injecting structured knowledge documents (hereafter "skills") into an LLM's context window can measurably improve coding performance on domain-specific tasks. We test this hypothesis using a paired experimental design across multiple models, skill formulations, and CLI environments.

Our research questions are:

1. **RQ1:** Do domain-specific skills improve budget model performance on coding tasks that require specialized knowledge?
2. **RQ2:** Does skill granularity matter --- do narrow, task-specific skills outperform broad reference documents?
3. **RQ3:** Can automated skill optimization (via DSPy compilation) produce skills that reliably help target models?
4. **RQ4:** Is skill uplift consistent across different CLI environments?

The scope of this study is limited to free and low-cost models available through OpenRouter (primarily the GLM and Qwen model families), two CLI environments (Claude Code and Kilo CLI), and two specialized domains (USD/Pixar composition and Houdini Solaris). All experiments were conducted over a four-day period (April 3--6, 2026) using a custom benchmarking framework.

---

## 2. Methodology

### 2.1 Framework Architecture

We developed **llm-bench**, a Python benchmarking framework that automates the execution, scoring, and comparison of LLM coding tasks across multiple CLI interfaces. The framework follows a src-layout package structure with async subprocess execution for parallel runs.

The core components are:

- **CLI Adapters** --- abstraction layer supporting Claude Code, Open Code, and Kilo CLI, each with provider-specific configuration (environment variables, model routing, context file format)
- **Workspace Manager** --- creates isolated temporary directories per run, copies task templates, injects skills into `.claude/skills/{name}/SKILL.md`, and writes CLI-specific context files (CLAUDE.md for Claude Code, AGENTS.md for Kilo)
- **Automated Scorer** --- executes each task's `validate.py` script against the model's output, returning scores on a 0.0--1.0 continuous scale
- **Result Storage** --- JSON files per run with model, CLI, task, score, timing, and raw output metadata

### 2.2 Four-Tier Task System

Tasks are organized into four tiers of increasing difficulty, with tiers 3 and 4 forming the core experimental pair:

| Tier | Purpose | Task Count | Skill Injected |
|------|---------|------------|----------------|
| 1 | Baseline sanity checks | 2 | No |
| 2 | General coding competence | 6 | No |
| 3 | Domain-specific (no skill) | 6 | No |
| 4 | Domain-specific (with skill) | 9 | Yes |

The key design decision is that **tier 3 and tier 4 tasks are identical in requirements**. The only variable changed between a tier 3 task and its tier 4 counterpart is the presence of a skill document. This paired design isolates skill uplift: the delta between tier 3 and tier 4 scores for the same model on the same task represents the causal effect of the skill.

### 2.3 Skill Injection Mechanism

Skills are injected via the `.claude/skills/{name}/SKILL.md` path, which is the native skill discovery mechanism shared by all three supported CLIs. A **variant system** allows multiple formulations of the same skill to be tested: the format `domain:variant` resolves to `skills/{domain}/{variant}.md`, with `VARIANTS.yaml` declaring available variants and their metadata.

### 2.4 DSPy Skill Compilation

To test automated skill optimization, we integrated DSPy's BootstrapFewShot optimizer. A teacher model (typically a stronger model) generates candidate skill documents, which are evaluated against either:

- **Proxy metric** --- a structural quality score assessing markdown formatting, code example presence, conciseness, and API pattern coverage (fast, no benchmark execution required)
- **Live metric** --- actual benchmark execution of the candidate skill against the target model on the target task (slow but behaviorally grounded)

The optimizer iterates, selecting the highest-scoring skill document.

### 2.5 Scoring

All scoring is automated via per-task `validate.py` scripts that assess functional correctness. Scores are continuous on a 0.0--1.0 scale, where 1.0 indicates full correctness and 0.0 indicates complete failure. Partial credit is awarded for partially correct implementations (e.g., correct structure but incorrect API usage). An LLM-as-judge component exists in the framework but was not used in these experiments; all reported scores are from deterministic automated validation.

---

## 3. Experimental Setup

### 3.1 Models

Six models were tested, all accessed via OpenRouter:

| Model | Parameters | Cost | Functional |
|-------|-----------|------|------------|
| glm-4.5-air-free | Unknown | Free | Yes |
| glm-4.7-flash | Unknown | Free | Yes |
| glm-5 | Unknown | Free | Yes |
| qwen3-coder-free | Unknown | Free | No (all timeout) |
| qwen3-next-80b-free | ~80B | Free | No (all timeout) |
| qwen3-30b (paid) | 30B | Low | Yes |

Two of the five initially selected free models (qwen3-coder-free and qwen3-next-80b-free) timed out on every task across both CLIs, producing zero usable data (entry #007). The remaining experiments focus on the three GLM models and qwen3-30b.

### 3.2 CLI Environments

Two CLI environments were used:

- **Claude Code** --- Anthropic's official CLI, using `.env` file swapping for model selection. Injects additional context via hooks (superpowers SessionStart).
- **Kilo CLI** --- alternative CLI with Pyright LSP integration, provider-specific routing.

### 3.3 Tasks

The task set expanded from 2 (MVP) to 16 (V1 benchmark) to 23 (final) over the experimental period. Domain-specific tasks focused on two areas:

- **USD (Pixar Universal Scene Description)** --- shot assembly using composition arcs, variant sets, and reference layering
- **Houdini Solaris** --- LOP network construction using the `hou` Python API (tested via a mock module)

### 3.4 Skill Variants

Five USD composition skill variants and two Houdini Solaris variants were tested:

| Variant | Lines | Creation Method | Proxy Score |
|---------|-------|-----------------|-------------|
| `reference` | 144 | Manual (broad API reference) | N/A |
| `task-hints` | 40 | Manual (task-scoped) | N/A |
| `compiled-glm45` | 80 | DSPy proxy (teacher: glm-5) | 0.80 |
| `compiled-live-glm45` | 59 | DSPy live (teacher: glm-5) | 1.00 |
| `compiled-qwen3-30b` | 76 | DSPy proxy (teacher: glm-5) | 1.00 |
| `houdini-solaris` (ref) | 160 | Manual (full Solaris reference) | N/A |
| `houdini-compiled-qwen3` | 74 | DSPy proxy (teacher: glm-5) | 0.84 |

### 3.5 Experiment Timeline

| Date | Experiment | Runs |
|------|-----------|------|
| Apr 3 | Framework development, early testing | 32 |
| Apr 4--5 | V1 Benchmark (5 models x 2 CLIs x 16 tasks) | 160 |
| Apr 6 | Skill variant experiment (5 variants x 3 models x 2 CLIs) | 18 |
| Apr 6 | Qwen3-30b experiment (baselines + compiled variants) | 16 |
| | **Total** | **~259** |

---

## 4. Results

### 4.1 Experiment 1: V1 Benchmark (160 runs)

The full V1 benchmark ran 5 models across 2 CLIs on 16 tasks over 6.3 hours (entry #009). With two models non-functional, 96 runs produced usable data across three GLM models.

**Tier pass rates** validated the difficulty calibration:

| Tier | Pass Rate | Description |
|------|-----------|-------------|
| 1 | 92% | Baseline (hello-world, fizzbuzz) |
| 2 | 78% | General coding |
| 3 | 42% | Domain-specific, no skill |
| 4 | 25% | Domain-specific, with skill |

As observed in entry #010, the progressive difficulty drop confirms the tier system's design. Notably, the drop from tier 3 (42%) to tier 4 (25%) is counterintuitive --- tier 4 tasks include a skill that should theoretically help. This aggregate result is the first indication that skills are net-negative.

**Best overall model:** glm-5 on Claude Code achieved 12/16 task passes with an average score of 0.76.

**Hardest tasks:** expression-parser, lru-cache, and houdini-solaris achieved 0/18 passes across all models and CLIs.

#### 4.1.1 The Skill Harm Discovery

The most significant finding from V1 was the negative skill uplift on weaker models. As documented in entry #011:

| Model | CLI | Tier 3 (no skill) | Tier 4 (with skill) | Delta |
|-------|-----|--------------------|----------------------|-------|
| glm-4.5-air-free | Claude Code | 0.8 | 0.2 | **-0.6** |
| glm-5 | Claude Code | 0.0 | 1.0 | **+1.0** |

The same broad USD reference skill (144 lines) destroyed glm-4.5's performance while enabling glm-5 to solve a previously impossible task. Root cause analysis (entry #012) revealed that weaker models treat skill examples as authoritative templates and hallucinate similar-sounding APIs (e.g., `GetPrototypeStage`, `.edit()` instead of the correct `GetVariantEditContext()`). The skill provides enough context to make the model confident in incorrect approaches without providing sufficient constraint to prevent hallucination.

This observation led to the **capability threshold hypothesis** (entry #013): skills only help models that are strong enough to synthesize from examples but not strong enough to solve the task unaided.

### 4.2 Experiment 2: Skill Variant Experiment (18 runs)

To test whether skill formulation affects uplift, we benchmarked multiple variants across three models and two CLIs (entries #018--#025).

**Average uplift by variant (across all models and CLIs):**

| Variant | Avg Uplift | Lines |
|---------|------------|-------|
| `reference` | -0.20 | 144 |
| `task-hints` | -0.13 | 40 |
| `compiled-glm45` (proxy) | -0.10 | 80 |
| `compiled-live-glm45` (live) | varies | 59 |

Narrower skills consistently reduced harm but none achieved net-positive uplift on average (entry #019). The DSPy-compiled variants performed marginally better than the manual broad reference, suggesting that conciseness and task focus are beneficial properties.

#### 4.2.1 The CLI Confound

The most troubling finding from this experiment was the CLI confound (entry #020). The DSPy-compiled skill produced dramatically different results depending on the CLI:

| Model | Variant | Claude Code | Kilo | Delta (CC-Kilo) |
|-------|---------|-------------|------|-----------------|
| glm-4.5 | compiled-glm45 | varies | 0.1 -> 0.8 | opposite |
| glm-4.5 | compiled-live-glm45 | 0.2 -> 0.8 | varies | opposite |

Every variant that helped one CLI hurt or was neutral on the other (entry #025). Investigation into root causes (entry #021) identified three mechanisms:

1. **Kilo LSP false positives** --- Pyright flags all `pxr` (Pixar USD) API calls as errors, forcing the model into corrective iteration loops that may help or hurt depending on the model's ability to handle LSP feedback
2. **Claude Code proxy telemetry loss** --- OpenRouter models show empty `raw_output` and token counts, preventing efficiency analysis
3. **Claude Code hook bloat** --- superpowers SessionStart injects thousands of words of context, consuming the model's context budget before the task and skill are even considered

As noted in entry #022, this means the benchmark measures the combined system of model + skill + CLI environment, not skill uplift in isolation.

### 4.3 Experiment 3: CLI Confound Investigation

The CLI confound investigation (entries #021--#022) established that the benchmark is partially a measure of CLI tooling quality rather than pure model capability. While this makes the results more ecologically valid (practitioners always use models through a CLI), it complicates the isolation of skill uplift as an independent variable.

The practical implication is that **skill optimization may need to be CLI-specific, not just model-specific** (entry #025).

### 4.4 Experiment 4: Qwen3-30b Experiment (16 runs)

The qwen3-30b experiment (entries #026--#037) tested a paid, mid-range model that proved to be **above the capability threshold** for USD tasks.

**USD Shot Assembly scores by variant on Claude Code:**

| Variant | Score | Delta from No-Skill Baseline |
|---------|-------|------------------------------|
| No skill (tier 3) | 1.0 | --- |
| `reference` (144 lines) | 0.7 | -0.3 |
| `task-hints` (40 lines) | 0.9 | -0.1 |
| `compiled-glm45` (80 lines) | 0.9 | -0.1 |
| `compiled-live-glm45` (59 lines) | 0.1 | -0.9 |
| `compiled-qwen3-30b` (76 lines) | 0.0 | -1.0 |

Every skill variant hurt this model on Claude Code (entry #029). The model scored a perfect 1.0 without any skill, and its own DSPy-compiled skill (proxy score 1.00) produced the worst possible outcome (0.0). Root cause analysis (entry #030) showed the model hallucinated `LockVariant()` --- a non-existent API --- despite the skill explicitly demonstrating the correct `GetVariantEditContext()` pattern.

#### 4.4.1 The Skill Detail Paradox

Entry #031 documents a counterintuitive finding: more detailed skills caused more harm. The `compiled-glm45` variant (vague, with placeholder comments like `# configure mesh...`) scored 0.9, while the `compiled-qwen3-30b` variant (detailed, with full working code) scored 0.0. The vague skill let the model skip complex operations and pass through its own approach; the detailed skill encouraged the model to attempt operations it then hallucinated incorrectly.

#### 4.4.2 Cross-Model Transfer

The `compiled-glm45` variant, compiled for a different model entirely, outperformed the `compiled-qwen3-30b` variant compiled specifically for qwen3-30b (0.9 vs 0.0, entry #032). This suggests that cross-model transfer can outperform model-specific optimization, possibly because cross-model skills are less prescriptive and give the model more room to apply its own priors.

#### 4.4.3 Kilo Failure and Difficulty Ceiling

qwen3-30b scored 0.0 on every USD and Houdini task on Kilo, regardless of skill variant --- 11 runs, all failures (entry #035). The same model scored 1.0 on some of these tasks on Claude Code, confirming that the CLI environment can completely block an otherwise capable model.

Houdini Solaris tasks were above qwen3-30b's capability ceiling regardless of CLI or skill: 0/6 across all configurations (entry #036).

#### 4.4.4 Run-to-Run Variance

Entry #037 documents that the `task-hints` variant produced scores of both 0.0 and 0.9 for qwen3-30b on Claude Code across separate runs of the same configuration. This high variance undermines single-run conclusions and is a significant threat to validity.

---

## 5. Discussion

### 5.1 Capability Threshold Theory

The central finding of this study is the **capability threshold model** for skill uplift, refined across entries #013 and #034 into three distinct zones:

1. **Below threshold** --- The model cannot perform the task at all. Skill content adds noise to the context, and the model hallucinates from examples rather than learning from them. Result: **net harm**.

2. **At threshold** --- The model sometimes passes the task unaided. Narrow, task-specific skills can provide the missing knowledge to tip the balance. Result: **potential uplift** (the sweet spot).

3. **Above threshold** --- The model reliably passes the task without assistance. The skill competes with the model's correct internal priors, introducing conflicting signals that degrade performance. Result: **net harm**.

The evidence for this model is strongest in the paired comparison of glm-4.5 (below threshold: harmed by skills, entry #011) and glm-5 (at threshold for Houdini Solaris: helped from 0.0 to 1.0, entry #014) and qwen3-30b (above threshold for USD: harmed from 1.0 to as low as 0.0, entry #029).

### 5.2 The Skill Detail Paradox

A related finding is that **more correct and detailed skill content can produce worse outcomes** (entry #031). This paradox arises because detailed skills encourage models to attempt complex operations they then hallucinate, while vague skills allow models to route around complexity using their own (potentially simpler but correct) approaches. The implication is that skill authoring should optimize for the minimum viable information, not comprehensiveness.

### 5.3 Proxy Metric Limitations

The DSPy proxy metric --- optimizing for structural quality (markdown formatting, code examples, conciseness, API pattern coverage) --- proved not predictive of real-world performance (entry #033). The `compiled-qwen3-30b` skill achieved the maximum proxy score of 1.00 but produced the minimum real score of 0.0. Structural quality and behavioral compliance are orthogonal dimensions. Live-metric compilation, which uses actual benchmark execution in the optimization loop, produced more reliable results but at substantially higher cost (34 minutes vs seconds for proxy evaluation).

### 5.4 CLI as Confounding Variable

The CLI environment emerged as an unexpectedly dominant variable (entries #020--#022, #025). The mechanisms are varied (LSP integration, context injection, provider routing) but the effect is consistent: the same model-skill configuration can produce opposite outcomes on different CLIs. This has both methodological and practical implications:

- **Methodological:** Skill uplift cannot be measured in a CLI-independent way. Results are specific to the model-skill-CLI triple, not the model-skill pair.
- **Practical:** Organizations deploying skills must test against their specific CLI environment, not assume transferability.

### 5.5 Threats to Validity

This study has several significant limitations:

1. **Single-run variance.** Most configurations were tested with a single run. Entry #037 demonstrates that the same configuration can produce scores of 0.0 and 0.9, meaning individual data points may not be representative. Statistical significance testing requires multiple runs per configuration, which resource constraints prevented.

2. **Small model set.** Only four functional models were tested (three free GLM models and one paid Qwen model). The capability threshold theory requires validation across a broader range of model sizes and families.

3. **CLI confound.** The inability to isolate CLI effects from skill effects means that some observed "skill harm" may actually be "CLI harm amplified by skill presence."

4. **Domain specificity.** All domain-specific experiments used USD and Houdini tasks. These are niche domains with limited representation in training data. Results may not generalize to more common programming domains where models have stronger priors.

5. **Automated scoring only.** While deterministic, the `validate.py` scripts assess functional correctness against specific test cases. They do not capture code quality, maintainability, or partial understanding that an LLM judge might identify.

6. **No frontier baseline.** A frontier model (e.g., Claude Opus 4.6) was not included in these experiments, so we cannot quantify the absolute gap that skills are attempting to close.

---

## 6. Conclusion

### 6.1 Summary of Contributions

This study makes four contributions:

1. **The capability threshold model** --- We demonstrate that skill uplift follows a non-monotonic pattern: skills help only models near a narrow capability threshold and harm models both above and below it. This directly contradicts the intuitive assumption that skills universally help weaker models.

2. **The skill detail paradox** --- We show that more detailed and correct skill content can produce worse outcomes than vague or incomplete skills, because detailed content encourages models to attempt operations they then hallucinate.

3. **CLI as confounding variable** --- We identify the CLI environment as a dominant factor in skill uplift measurement, with identical model-skill pairs producing opposite results across different interfaces.

4. **Proxy metric failure** --- We demonstrate that DSPy proxy metrics optimizing for structural quality do not predict real-world skill effectiveness, achieving maximum proxy scores on skills that produced minimum real scores.

### 6.2 Implications for Practitioners

The primary practical implication is clear: **do not blindly inject domain knowledge into LLM coding workflows**. Specifically:

- Before adding skills, establish a no-skill baseline. If the model already solves the task reliably, adding skills will likely hurt.
- Prefer narrow, task-scoped skills over broad reference documents. Minimum viable information outperforms comprehensive coverage.
- Test skills against the specific CLI environment in which they will be deployed. Do not assume cross-CLI transferability.
- Do not trust proxy metrics for skill quality. Only live evaluation against the target model on the target task provides reliable signal.

### 6.3 Future Work

Several directions emerge from this study:

1. **Multi-run statistical validation** --- Repeat key experiments with 5--10 runs per configuration to establish confidence intervals and statistical significance.
2. **Frontier model baseline** --- Include Claude Opus 4.6 or equivalent to quantify the absolute frontier gap.
3. **Adaptive skill injection** --- Develop a predictor that estimates whether a model is at the capability threshold for a given task before deciding whether to inject a skill.
4. **CLI isolation** --- Design experiments that control for CLI effects, potentially using a minimal CLI wrapper that adds no additional context.
5. **Broader domains** --- Extend to more common programming domains (web development, data science) where models have stronger priors and the threshold dynamics may differ.
6. **Skill titration** --- Systematically vary skill detail level to map the relationship between information density and uplift across the capability spectrum.

---

## Appendix A: Skill Variant Summary

### A.1 USD Composition Variants

| Variant | Lines | Method | Target Model | Proxy Score | Key Property |
|---------|-------|--------|-------------|-------------|--------------|
| `reference` | 144 | Manual | General | N/A | Broad API reference covering composition arcs, variant sets, references, payloads |
| `task-hints` | 40 | Manual | General | N/A | Task-scoped; only APIs needed for shot assembly |
| `compiled-glm45` | 80 | DSPy proxy | glm-4.5-air-free | 0.80 | Proxy-optimized; placeholder comments, moderate detail |
| `compiled-live-glm45` | 59 | DSPy live | glm-4.5-air-free | 1.00 | Live-metric optimized on Kilo; most concise compiled variant |
| `compiled-qwen3-30b` | 76 | DSPy proxy | qwen3-30b | 1.00 | Proxy-optimized; full working code examples, high detail |

### A.2 Houdini Solaris Variants

| Variant | Lines | Method | Target Model | Proxy Score | Key Property |
|---------|-------|--------|-------------|-------------|--------------|
| `SKILL` (reference) | 160 | Manual | General | N/A | Full Solaris LOP reference |
| `compiled-qwen3-30b` | 74 | DSPy proxy | qwen3-30b | 0.84 | Proxy-optimized; task-focused code patterns |

### A.3 Cross-Reference: Skill Variant Performance on USD Shot Assembly (Claude Code)

| Variant | glm-4.5-air-free | glm-4.7-flash | glm-5 | qwen3-30b |
|---------|-------------------|---------------|-------|-----------|
| No skill (tier 3) | 0.8 | -- | -- | 1.0 |
| `reference` | 0.2 | -- | -- | 0.7 |
| `task-hints` | -- | -- | -- | 0.9 |
| `compiled-glm45` | -- | -- | -- | 0.9 |
| `compiled-live-glm45` | 0.8 | -- | -- | 0.1 |
| `compiled-qwen3-30b` | -- | -- | -- | 0.0 |

*Note: "--" indicates configuration was not tested or data was not recorded in the experiment log. Scores represent single runs unless otherwise noted.*

## Appendix B: Log Entry Index

| Entry | Date | Category | Title |
|-------|------|----------|-------|
| #001 | 2026-04-03 | Method | Framework design --- 4-tier task system |
| #002 | 2026-04-03 | Method | Skill injection via .claude/skills/ |
| #003 | 2026-04-03 | Context | Core research question defined |
| #004 | 2026-04-03 | Context | MVP framework implemented |
| #005 | 2026-04-03 | Result | Early dev runs (32 runs) |
| #006 | 2026-04-04 | Method | Selected 5 free/cheap OpenRouter models |
| #007 | 2026-04-04 | Finding | 2 of 5 free models non-functional |
| #008 | 2026-04-05 | Method | Expanded to 16 tasks |
| #009 | 2026-04-05 | Result | V1 Benchmark --- 160 runs, 6.3 hours |
| #010 | 2026-04-05 | Finding | Tier difficulty calibrated: 92/78/42/25% |
| #011 | 2026-04-05 | Surprise | Broad skill destroys glm-4.5 (0.8 to 0.2) |
| #012 | 2026-04-05 | Finding | Root cause: hallucination amplification |
| #013 | 2026-04-05 | Hypothesis | Capability threshold theory |
| #014 | 2026-04-05 | Surprise | glm-5 + houdini skill: 0.0 to 1.0 |
| #015 | 2026-04-05 | Method | Skill variant system |
| #016 | 2026-04-05 | Method | Task-hints variant (40 lines) |
| #017 | 2026-04-05 | Method | DSPy skill compiler |
| #018 | 2026-04-06 | Result | DSPy proxy compilation for glm-4.5 |
| #019 | 2026-04-06 | Result | Variant experiment --- all net-negative |
| #020 | 2026-04-06 | Surprise | Same model+skill opposite on different CLIs |
| #021 | 2026-04-06 | Finding | CLI confound root causes |
| #022 | 2026-04-06 | Finding | Benchmark measures CLI tooling too |
| #023 | 2026-04-06 | Result | DSPy live-metric compilation (34 min) |
| #024 | 2026-04-06 | Result | 18 variant runs --- 5 variants benchmarked |
| #025 | 2026-04-06 | Finding | No single variant works across CLIs |
| #026 | 2026-04-06 | Result | Qwen3-30b baseline benchmarks (12 runs) |
| #027 | 2026-04-06 | Result | DSPy compilation targeting qwen3-30b |
| #028 | 2026-04-06 | Result | Compiled variant benchmarks --- 0/4 pass |
| #029 | 2026-04-06 | Surprise | qwen3-30b: 1.0 without, 0.0 with own skill |
| #030 | 2026-04-06 | Finding | Hallucinated LockVariant() despite skill |
| #031 | 2026-04-06 | Finding | Skill detail paradox |
| #032 | 2026-04-06 | Finding | Cross-model transfer outperforms specific |
| #033 | 2026-04-06 | Finding | DSPy proxy metric not predictive |
| #034 | 2026-04-06 | Hypothesis | Skill harm zones refined |
| #035 | 2026-04-06 | Finding | Kilo 0.0 on all for qwen3-30b |
| #036 | 2026-04-06 | Finding | Houdini Solaris above difficulty ceiling |
| #037 | 2026-04-06 | Finding | Run-to-run variance is high |
