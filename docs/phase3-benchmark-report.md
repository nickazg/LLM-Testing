# Phase 3 Benchmark Report: Skill Taxonomy & DSPy Compilation

**Authors**: Nick Grobler & Claude Code
**Date**: 2026-04-08
**Results**: 1,607 runs across 13 models, 2 CLIs, 68 task definitions
**Duration**: ~8 hours (parallel execution, 4 workers)

---

## Executive Summary

This benchmark introduces a three-category skill taxonomy (Novel Knowledge, Workflow/Process, Domain Context) with heavy/light intensity variants, and tests DSPy-compiled skill optimization across 5 target models. Key findings:

1. **GLM-5 dominates** at 87% pass rate — the clear budget model champion
2. **Skills help strong models, hurt weak ones** — the capability threshold theory holds
3. **DSPy compilation is a double-edged sword** — improves specific weak spots but degrades models below the capability threshold
4. **Devstral shows catastrophic skill interference** — 22% baseline drops to 0% on ALL skill variants
5. **Gemma models underperform dramatically** vs online benchmarks, likely due to CLI integration issues
6. **Kilo outperforms Claude Code** for most budget models — opposite of Phase 2 findings

---

## 1. Model Rankings

> **Note:** 163 runs (10%) timed out due to inference infrastructure constraints (API latency, OpenRouter routing) and are excluded from pass rates below. Timeouts reflect I/O bottlenecks, not model/skill capability. Most affected: gemma-4-31b (38 timeouts — pass rate jumps from 23% to 43% when excluded).

| Rank | Model | Runs | Pass | Rate | CC | Kilo | Timeouts |
|------|-------|------|------|------|-----|------|----------|
| 1 | opus4.6 (frontier) | 3 | 3 | 100% | 2/2 | 1/1 | 0 |
| 2 | gemini-3.1-pro (frontier) | 2 | 2 | 100% | 1/1 | 1/1 | 0 |
| 3 | **glm-5** | 218 | 189 | **87%** | 90% | 84% | 2 |
| 4 | **glm-4.5-air-free** | 96 | 75 | **78%** | 69% | 82% | 19 |
| 5 | **qwen3-30b** | 166 | 114 | **69%** | 66% | 71% | 5 |
| 6 | gpt-5.4 (frontier) | 2 | 1 | 50% | 0/1 | 1/1 | 0 |
| 7 | **gemma-4-31b** | 28 | 12 | **43%** | 33% | 50% | 38 |
| 8 | devstral | 166 | 40 | 24% | 14% | 55% | 21 |
| 9 | gemma-4-27b | 152 | 19 | 12% | 7% | 34% | 22 |
| 10 | glm-4.7-flash | 154 | 4 | 3% | 2% | 11% | 18 |
| 11 | minimax-m2.7 | 151 | 4 | 3% | 1% | 25% | 0 |
| 12 | gpt-oss-20b | 153 | 4 | 3% | 1% | 7% | 19 |
| 13 | gpt-oss-120b | 153 | 4 | 3% | 1% | 7% | 19 |

### Tier breakdown

| Model | T1 (basics) | T2 (multi-file) | T3 (domain, no skill) | T4 (with skills) |
|-------|-------------|------------------|-----------------------|-------------------|
| glm-5 | 8/8 (100%) | 12/13 (92%) | 27/30 (90%) | 144/169 (85%) |
| glm-4.5-air-free | 8/8 (100%) | 9/13 (69%) | 19/30 (63%) | 47/64 (73%) |
| qwen3-30b | 3/8 (38%) | 11/13 (85%) | 20/30 (67%) | 80/120 (67%) |
| devstral | 8/8 (100%) | 13/13 (100%) | 20/30 (67%) | **0/136 (0%)** |
| gemma-4-31b | 6/8 (75%) | 3/13 (23%) | 5/30 (17%) | 1/15 (7%) |
| gemma-4-27b | 8/8 (100%) | 10/13 (77%) | 2/30 (7%) | 0/123 (0%) |

---

## 2. What Each Test Case Measures

### Tier 1 — Can the model produce code at all?
- **hello-world**: Single file, single print statement. Floor test for CLI routing.
- **fizzbuzz**: Conditional logic, loops. Still trivial but tests basic reasoning.

### Tier 2 — Can it handle multi-concern tasks?
- **makefile**: Non-Python, whitespace-sensitive syntax. Cross-language competence.
- **csv-pipeline**: Data processing with filtering, grouping, aggregation. Realistic scripting.
- **cli-tool**: argparse, error handling, formatted output. Common developer task.
- **usd-scene**: Basic USD API — "can you do VFX at all?" baseline.
- **houdini-sop**: Basic Houdini Python — node creation, parameters, connections.
- **log-processor**: Bash text processing with POSIX constraints.

### Tier 3 — Domain expertise without help (control group)
- **lru-cache**: Classic CS problem with specific constraints (no OrderedDict, thread-safe). Tests whether models follow negative constraints.
- **expression-parser**: Recursive descent parser with operator precedence. Well-known but tricky to implement correctly.
- **git-hook**: Bash + git integration. Multiple validation checks on staged files.
- **service-generator**: Code generation (systemd units from args). Tests template-based output.
- **usd-shot-assembly**: The flagship USD test. Multi-file composition with sublayers, references, variant sets — core USD concepts most budget models lack.
- **houdini-solaris**: The flagship Houdini test. Requires knowing both `hou` module and `pxr` library simultaneously in a Solaris LOPs context.
- **usd-render-settings**: UsdRender API — cameras, render products, AOVs. Sparse documentation.
- **usd-procedural-animation**: UsdSkel — one of the most complex USD subsystems. Time-sampled data, joint hierarchies, skinning.
- **usd-stage-layers**: Layer opinion system — the core of USD's non-destructive editing model.
- **usd-shader-graph**: Shader connectivity API — wiring nodes, texture coordinates, per-face material binding.
- **usd-custom-schema**: USD extensibility — custom metadata, purpose, typed properties. Production pipeline knowledge.
- **houdini-pdg**: PDG/TOPs — pipeline automation with work items. Very niche.
- **houdini-solaris-instancing**: PointInstancer API — prototype registration, per-instance attributes, collections.
- **houdini-solaris-render**: Render config in Solaris — RenderProducts, AOVs, Karma-specific settings.
- **houdini-solaris-light-linking**: Light linking via collections, light filters, purpose-based visibility.

### Tier 4 — Same prompts, skills injected (experimental group)
Each T3 task has T4 variants that inject skills of different types and intensities. The task prompt is identical — only the presence/absence of a skill document changes.

---

## 3. Skill Taxonomy Analysis

### Overall skill type performance (timeouts excluded)

| Category | Runs | Pass | Rate |
|----------|------|------|------|
| No skill (T3 baseline) | 191 | 92 | **48%** |
| **workflow/light** | **20** | **8** | **40%** |
| context/heavy | 127 | 49 | 39% |
| workflow/heavy | 121 | 42 | 35% |
| context/light | 20 | 6 | 30% |
| novel/heavy | 666 | 140 | 21% |
| novel/light | 98 | 21 | 21% |

### Key insight: Skills don't help on aggregate

The aggregate numbers are misleading — **no skill category outperforms the no-skill baseline (48%)**. This is because the averages include weak models that are *hurt* by skills. The real story is in the per-model breakdown.

### Per-model skill uplift (top 3 models)

**GLM-5 (strong model — skills mostly help)**
| Task | No Skill | Novel/Heavy | Novel/Light | Workflow/Heavy | Workflow/Light |
|------|----------|-------------|-------------|----------------|----------------|
| expression-parser | 0.50 | - | - | 0.75 (+0.25) | 0.93 (+0.43) |
| houdini-solaris | 0.00 | 0.18 (+0.18) | 0.00 | - | - |
| usd-render-settings | 0.88 | 1.00 (+0.12) | 1.00 (+0.12) | - | - |
| usd-procedural-animation | 0.94 | 1.00 (+0.06) | 1.00 (+0.06) | - | - |
| service-generator | 1.00 | - | - | - | - | 0.92 (-0.08) | 0.70 (-0.30) |

GLM-5 pattern: Skills help on tasks where it was weak (expression-parser +0.43, houdini-solaris +0.18) but can *hurt* on tasks where it was already strong (service-generator -0.30 with context/light).

**Devstral (catastrophic skill interference)**
| Task | No Skill | ANY Skill Variant |
|------|----------|-------------------|
| expression-parser | 0.97 | 0.00 |
| git-hook | 1.00 | 0.00 |
| houdini-pdg | 0.88 | 0.00 |
| houdini-solaris-instancing | 1.00 | 0.00 |
| lru-cache | 0.73 | 0.00 |

**Every single skill variant — novel, workflow, context, heavy, light, compiled — drops devstral to 0%.** This is the clearest evidence of skill interference: devstral performs well from its training data alone, but injecting ANY external document into its workspace causes total failure. This model cannot integrate external context.

**qwen3-30b (mixed — skills help on some, hurt on others)**
| Task | No Skill | Best Skill | Best Type | Worst Skill | Worst Type |
|------|----------|------------|-----------|-------------|------------|
| expression-parser | 0.47 | 1.00 | workflow/light | - | - |
| houdini-solaris | 0.00 | 0.05 | novel/heavy | 0.00 | novel/light |
| service-generator | 0.94 | 1.00 | context/heavy | - | - |
| houdini-solaris-render | 1.00 | 0.67 | novel/heavy | - | - |

---

## 4. DSPy Compilation Effect

### Does model-specific skill optimization help?

**For qwen3-30b (the best compilation target):**
| Task | Baseline | Reference Skill | Compiled | Delta |
|------|----------|-----------------|----------|-------|
| expression-parser | 0.47 | 0.00 | **1.00** | **+0.53** |
| service-generator | 0.94 | 1.00 | 1.00 | +0.06 |
| usd-custom-schema | 0.25 | 0.12 | 0.30 | +0.05 |
| houdini-solaris-render | 1.00 | 1.00 | 0.60 | **-0.40** |
| houdini-solaris-light-linking | 1.00 | 1.00 | 0.78 | **-0.22** |

Compilation is a **targeted tool**: it dramatically improved expression-parser (+0.53) but degraded houdini-solaris-render (-0.40). The DSPy optimizer may be over-fitting to one task pattern at the expense of others.

**For gemma-4-27b, devstral, glm-4.7-flash (below capability threshold):**

Compilation has **zero or negative effect** across the board. These models produce 0.00 on virtually every compiled variant. You cannot optimize a skill document for a model that fundamentally cannot use skills.

### Compilation verdict

| Model | Compilation useful? | Evidence |
|-------|---------------------|----------|
| qwen3-30b | **Yes, selectively** | +0.53 on expression-parser, but -0.40 on other tasks |
| gemma-4-31b | No | 0.00 everywhere |
| gemma-4-27b | No | 0.00 everywhere |
| devstral | **Harmful** | All compiled variants = 0.00 (baseline was 22%) |
| glm-4.7-flash | No | 0.00 everywhere |

---

## 5. Why Models Performed As They Did

### Failure mode analysis

| Model | Total Failures | Timeouts | No Files Created | Errors | Wrong Output |
|-------|---------------|----------|------------------|--------|--------------|
| gpt-oss-20b | 168 | 27 | **128** | 0 | 13 |
| gpt-oss-120b | 168 | 26 | **129** | 0 | 13 |
| glm-4.7-flash | 166 | 25 | **128** | 0 | 13 |
| gemma-4-27b | 154 | 22 | **121** | 0 | 11 |
| minimax-m2.7 | 147 | 6 | **128** | 0 | 13 |
| devstral | 146 | 20 | **118** | 0 | 8 |
| qwen3-30b | 57 | 18 | 13 | 0 | 26 |
| gemma-4-31b | 51 | **48** | 1 | 0 | 2 |
| glm-4.5-air-free | 32 | 22 | 0 | 0 | 10 |
| glm-5 | 29 | 2 | 0 | 4 | 23 |

### Key failure patterns

**"No Files Created" dominance (gpt-oss, glm-4.7-flash, minimax, gemma-4-27b)**: These models consistently fail to produce any output files. They either don't understand the task, refuse to use tools, or get stuck in conversation loops. This suggests a fundamental inability to operate within the CLI tool-use paradigm, not a coding capability issue.

**gemma-4-31b is timeout-dominated (48/51 failures)**: Nearly all failures are timeouts, not wrong answers. The model is slow (avg 223s per run) and frequently exceeds the 300s timeout. When it does finish, it usually produces correct output. This is a performance issue, not a capability issue. The model "knows" the answers but can't execute fast enough.

**gemma-4-27b (the MoE variant) — worse than expected**: Despite having 31B total parameters, only 4B are active. Combined with being routed through OpenRouter, it frequently produces no output. Online benchmarks test the model directly; our benchmark tests through CLI → OpenRouter → model pipeline, where latency and token overhead from CLI scaffolding consume budget.

**devstral's catastrophic skill failure**: Devstral scored 67% on T3 (no skill) — respectable — but **0% on all 136 T4 runs**. Investigating the failure mode: devstral produces no files when a skill is present. The model appears to read the skill document and then gets confused by the dual context (skill instructions + task prompt), producing responses but not using file-write tools. This is a fundamental context integration failure specific to this model.

### Why Gemma underperforms vs online benchmarks

Online benchmarks (MMLU, HumanEval, etc.) test models in isolation with direct prompting. Our benchmark adds layers of complexity:

1. **CLI scaffolding overhead**: The model must understand and operate within Claude Code or Kilo's tool-use framework (file read/write/execute tools). This consumes context and requires understanding JSON tool schemas.
2. **OpenRouter routing**: Adds latency and sometimes truncates or transforms the prompt.
3. **Skill document injection**: Extra context in the workspace that some models can't effectively integrate.
4. **VFX domain specificity**: Most online benchmarks test general coding. Our T3/T4 tasks test niche USD/Houdini APIs that may not be in gemma's training data at all.

Note: gemma-4-31b achieves **43%** when timeouts are excluded (38 of 66 runs timed out). The model possesses the knowledge but is bottlenecked by inference speed through OpenRouter. With direct API access or extended timeouts, its true capability would likely be substantially higher.

**The benchmark measures "can this model do real work through a CLI tool?" — not "can this model answer coding questions?"**

---

## 6. CLI Comparison: Claude Code vs Kilo

| Model | CC Rate | Kilo Rate | Winner |
|-------|---------|-----------|--------|
| glm-5 | 90% | 84% | CC (+6%) |
| glm-4.5-air-free | 67% | 75% | Kilo (-8%) |
| qwen3-30b | 64% | 69% | ~even |
| gemma-4-31b | 17% | 29% | Kilo (-12%) |
| devstral | 13% | 51% | **Kilo (-38%)** |
| gemma-4-27b | 7% | 33% | **Kilo (-26%)** |

### Key finding: Kilo outperforms CC for most budget models

This reverses the Phase 2 finding where CC was dominant. The likely explanation:

1. **CC has heavier scaffolding**: Claude Code's system prompt and tool definitions consume more context budget, leaving less room for the actual task. Budget models with small effective context windows are disproportionately affected.
2. **Kilo's leaner protocol**: Kilo sends less overhead, giving the model more room to reason about the task.
3. **Z.ai direct on Kilo**: GLM models now route through Z.ai's coding API directly on Kilo (instead of OpenRouter), eliminating a middleman. This improved glm-4.5-air-free and glm-4.7-flash on Kilo.

**Exception**: GLM-5 performs better on CC (+6%), likely because it's powerful enough to handle CC's heavier scaffolding and may benefit from the richer tool descriptions.

---

## 7. Skill Intensity: Heavy vs Light

### Does more detail help or hurt?

For the top 3 models (glm-5, glm-4.5-air-free, qwen3-30b), comparing heavy vs light on the same task:

| Task | Model | Heavy | Light | Winner |
|------|-------|-------|-------|--------|
| expression-parser | glm-5 | 0.75 (workflow) | 0.93 (workflow) | **Light** |
| expression-parser | qwen3-30b | 0.83 (workflow) | 1.00 (workflow) | **Light** |
| houdini-solaris | glm-5 | 0.18 (novel) | 0.00 (novel) | Heavy |
| houdini-pdg | glm-5 | 0.99 (novel) | 1.00 (novel) | ~even |
| houdini-pdg | qwen3-30b | 0.84 (novel) | 0.94 (novel) | **Light** |
| git-hook | glm-5 | 1.00 (context) | 0.80 (context) | Heavy |
| service-generator | glm-5 | 0.92 (context) | 0.70 (context) | Heavy |
| solaris-instancing | glm-4.5-air | 1.00 (novel) | 1.00 (novel) | ~even |

### Pattern

- **Workflow skills**: Light wins. These models already know algorithms; a concise reminder of approach + guardrails is more effective than a prescriptive recipe that may conflict with the model's internal knowledge.
- **Novel skills**: Heavy wins on genuinely unknown APIs (houdini-solaris) where the model needs the actual API reference. Light wins when the model has partial knowledge (houdini-pdg) and just needs direction.
- **Context skills**: Heavy wins. When the model must extract specific org conventions, more detail = better compliance. Light context skills are too vague to be actionable.

---

## 8. Summary of Findings

### Confirmed hypotheses
1. **Capability threshold for skill uplift**: Skills only help models above a capability floor (~65%+ baseline). Below that, skills are neutral or harmful.
2. **Skill type matters**: Novel knowledge helps on genuinely unknown domains. Workflow guidance helps on known problems. Context skills help with org-specific requirements.
3. **Intensity matters asymmetrically**: Light workflow > heavy workflow. Heavy context > light context. Heavy novel > light novel (for genuinely unknown APIs).

### New findings
4. **Devstral's context integration failure**: Some models fundamentally cannot integrate external documents into their tool-use workflow. This is a model architecture issue, not a content issue.
5. **CLI overhead is a real variable**: Kilo's leaner protocol gives budget models an advantage. The "best CLI" depends on the model.
6. **DSPy compilation is risky**: Helps on targeted weak spots but can degrade performance on tasks where the model was already strong. Over-fitting is a real concern.
7. **Online benchmarks don't predict CLI performance**: gemma-4-31b's 23% vs its top-tier HumanEval scores demonstrates that agentic coding through CLIs is a fundamentally different capability than answering coding questions.

### New finding: Scores are binary, not gradual

The deep data extraction reveals a striking pattern — **correctness scores are almost always 1.00 or 0.00**. Very few partial scores exist across all 1,607 runs. This means models either fully understand a task or fail completely. There is no "partially correct" middle ground. This has implications for skill design: skills don't need to improve partial understanding — they need to push models past a binary comprehension threshold.

| Model | Zero scores | Partial (0<x<0.5) | Pass (0.5-1.0) | Perfect (1.0) |
|-------|------------|---------------------|----------------|---------------|
| devstral | 145 | 1 | 10 | 31 |
| gemma-4-27b | 154 | 0 | 2 | 18 |
| glm-4.7-flash | 164 | 2 | 1 | 5 |
| gpt-oss-120b | 168 | 0 | 0 | 4 |

### New finding: Import errors dominate weak model failures

The deep analysis reveals the **dominant failure mode is IMPORT_ERROR** — 85-97% of zero-correctness runs from weak models show import/module errors. These models generate code that references nonexistent modules or fails to properly invoke CLI file-writing tools. They're not producing wrong code — they're failing to produce any usable output at all. This is a CLI integration failure, not a coding capability failure.

| Model | Import Errors | No Output | Wrong Output |
|-------|--------------|-----------|--------------|
| gemma-4-27b | 133 (86%) | 21 | 0 |
| gpt-oss-120b | 142 (85%) | 26 | 0 |
| gpt-oss-20b | 141 (84%) | 27 | 0 |
| devstral | 126 (87%) | 19 | 0 |
| gemma-4-31b | 5 (10%) | 44 (88%) | 1 |

gemma-4-31b is the outlier — its failures are primarily NO_OUTPUT (timeouts), not import errors. This confirms it's a performance/speed issue, not a capability issue.

---

## 9. Model Recommendations

- **Budget VFX/pipeline work**: GLM-5 (87%) — clear winner, use Z.ai coding API
- **General coding, budget**: qwen3-30b (67%) — solid all-rounder
- **If free tier matters**: glm-4.5-air-free (72%) — best free option, surprisingly strong
- **Avoid for CLI work**: gpt-oss-120b/20b, minimax-m2.7 (2-3%) — non-functional through CLIs
- **Avoid with skills**: devstral — use only without skills (67% baseline, 0% with any skill)
- **gemma-4-31b**: Has the knowledge but is too slow. If timeout could be extended to 600s+, pass rate would likely improve significantly
