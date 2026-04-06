# Skill Uplift in Budget LLMs: How CLI Environment Determines Whether Structured Knowledge Helps or Destroys Coding Performance

**Authors:** Nick Grobler  
**Date:** April 2026  
**Framework:** llm-bench v0.1  
**Total runs:** 746 across 2 phases (478 Phase 2 primary, 268 Phase 1 archived)  

---

## Abstract

Can structured domain knowledge ("skills") close the coding performance gap between budget and frontier large language models? We present a controlled benchmarking study using a purpose-built framework (llm-bench) that measures skill uplift across 33 tasks, 8 models, and 2 CLI environments over 746 total runs. Our primary dataset of 478 Phase 2 runs across 266 paired skill uplift comparisons reveals that the CLI environment --- not the skill content or model capability --- is the dominant variable determining whether skills help or harm. On Claude Code, skills produce a mean uplift of +0.147 (40 positive, 84 neutral, 9 negative outcomes). On Kilo CLI, the same skills produce a mean uplift of -0.068 (9 positive, 95 neutral, 29 negative). Identical model-skill pairs produce opposite outcomes depending on the CLI: the Houdini Solaris skill lifts three models from 0.0 to 1.0 on Claude Code while producing zero improvement on Kilo; the expression parser skill yields +1.0 and -1.0 swings for the same model across CLIs. We also document extreme model-CLI coupling asymmetries --- qwen3-coder-next passes 21/33 tasks on Claude Code but 0/33 on Kilo, while gemma-4-31b shows the inverse pattern (0/33 CC, 7/33 Kilo). These findings refine our earlier capability threshold theory: while the model's position relative to a task-specific capability threshold still governs susceptibility to skill effects, the CLI environment determines the direction of that effect. Blindly injecting domain knowledge into LLM coding workflows remains counterproductive without CLI-specific validation.

---

## 1. Introduction

The rapid proliferation of LLM-powered coding assistants has created a practical question for organizations with budget constraints: can structured domain knowledge compensate for using smaller, cheaper models instead of frontier systems? If a 30-billion-parameter model armed with the right reference material could match a frontier model's output on domain-specific tasks, the cost implications would be significant.

This paper investigates the **skill uplift hypothesis**: that injecting structured knowledge documents (hereafter "skills") into an LLM's context window can measurably improve coding performance on domain-specific tasks. We test this hypothesis using a paired experimental design across multiple models, skill formulations, and CLI environments, drawing on 746 runs across two experimental phases.

Our research questions are:

1. **RQ1:** Do domain-specific skills improve budget model performance on coding tasks that require specialized knowledge?
2. **RQ2:** Does skill granularity matter --- do narrow, task-specific skills outperform broad reference documents?
3. **RQ3:** Can automated skill optimization (via DSPy compilation) produce skills that reliably help target models?
4. **RQ4:** Is skill uplift consistent across different CLI environments?

Phase 1 (268 runs, April 3--6, 2026) was exploratory: framework development, hypothesis generation, and methodology refinement across 4 models and 16 tasks. It produced the initial capability threshold theory and the skill detail paradox. Phase 2 (478 runs, April 6--7, 2026) is the definitive benchmark: clean data across 8 models (7 budget + 1 frontier ceiling), 33 tasks, and 2 CLIs. Phase 2 confirmed some Phase 1 hypotheses, overturned others, and revealed the CLI environment as the dominant variable --- a finding that Phase 1's smaller dataset only hinted at.

The scope of this study is limited to free and low-cost models available through OpenRouter (primarily the GLM, Qwen, Gemma, and MiniMax model families), one frontier ceiling model (Claude Opus 4.6), two CLI environments (Claude Code and Kilo CLI), and specialized domains including USD/Pixar composition, Houdini Solaris, recursive descent parsing, and LRU cache implementation. All experiments were conducted over a five-day period (April 3--7, 2026) using a custom benchmarking framework.

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
| 4 | Domain-specific (with skill) | 19 | Yes |

The key design decision is that **tier 3 and tier 4 tasks are identical in requirements**. The only variable changed between a tier 3 task and its tier 4 counterpart is the presence of a skill document. This paired design isolates skill uplift: the delta between tier 3 and tier 4 scores for the same model on the same task represents the causal effect of the skill.

#### 2.2.1 Task Descriptions

Each task is a self-contained directory containing a `task.yaml` definition, a `template/` directory of starting files copied into the workspace, and a `validate.py` scoring script. The model receives the task prompt and must produce working code in an isolated temporary directory.

**Tier 1 --- Baseline Sanity Checks** test fundamental code generation capability:

- **hello-world**: Create a Python file that prints "Hello, World!". The simplest possible code generation task, validating that the CLI-to-model pipeline produces executable output.
- **fizzbuzz**: Print numbers 1-100 with FizzBuzz substitutions. Tests basic logic, loops, and conditionals.

**Tier 2 --- General Coding Competence** tests real-world programming patterns without domain-specific knowledge:

- **csv-pipeline**: Read, transform, and aggregate CSV data using Python's standard library.
- **cli-tool**: Build a `wc`-like word count tool with argparse flags (`--lines`, `--words`, `--chars`) and multi-file totals.
- **log-processor**: Write a POSIX-compatible bash script that parses Apache access logs, extracting top IPs, status codes, and paths.
- **makefile**: Create a multi-target Makefile for a C project with compilation, testing, and installation targets using automatic variables.
- **usd-scene**: Build a simple USD scene with geometry, materials, and lighting using the Pixar `pxr` library. This tier 2 task tests basic USD API usage without composition complexity.
- **houdini-sop**: Create a Houdini SOP network script that builds geometry and sets HDA parameters. Tested via a mock `hou` module that tracks API calls.

**Tier 3 --- Domain-Specific Tasks** require niche knowledge that budget models may lack. These form the control group for the skill uplift experiment:

- **expression-parser**: Implement a mathematical expression parser with AST construction and evaluation. Requires understanding of recursive descent parsing, operator precedence, and tree evaluation. The validator tests 20 cases including edge cases (unary minus, nested parentheses, division by zero).
- **lru-cache**: Implement an LRU cache with O(1) `get`/`put` operations using a dict + doubly-linked list (not OrderedDict). Must be thread-safe with `threading.Lock`. The validator tests 15 criteria including capacity eviction, thread safety, and implementation constraints.
- **git-hook**: Write a bash pre-commit hook that validates staged files for size limits, debug print statements, trailing whitespace, and Python syntax errors.
- **service-generator**: Generate valid systemd service unit files from command-line arguments with proper `[Unit]`, `[Service]`, and `[Install]` sections.
- **usd-shot-assembly**: Build a multi-file USD shot assembly with cross-file references, variant sets (model variants and lighting variants), and transform operations. This is the primary skill uplift task --- it requires knowledge of USD composition arcs (`GetVariantEditContext`, sublayers, references) that budget models frequently hallucinate.
- **houdini-solaris**: Implement a Houdini Solaris Python Script LOP that builds a complete scene: root hierarchy, ground plane mesh, hero body cube, distant and dome lighting, PBR materials with shader binding, and model kind assignment. Requires 10 specific USD operations through the `hou.pwd().editableStage()` pattern.

**Tier 4 --- Paired Skill Tasks** are clones of tier 3 tasks with a skill document injected. Each shares the identical prompt, template, and validator as its tier 3 counterpart. The only change is the `skill` field in `task.yaml`:

- **usd-shot-assembly** (5 variants): Tests 5 different skill formulations for the same USD task --- reference, task-hints, compiled-glm45, compiled-live-glm45, and compiled-qwen3-30b
- **houdini-solaris** (2 variants): Tests reference and compiled-qwen3-30b skills
- **expression-parser**: Tests the recursive-descent-parser skill
- **lru-cache**: Tests the lru-cache-pattern skill

#### 2.2.2 Example: What a Task Looks Like

To illustrate the experimental setup concretely, here is the prompt for the core USD shot assembly task (used identically for tier 3 and all tier 4 variants):

> *Create a Python script called assemble_shot.py that uses the pxr library (Pixar USD) to build a multi-file shot assembly. The script must create TWO files:*
>
> *1. assets.usda --- contains: Default prim /Assets, /Assets/Chair with a child Mesh, and a variant set 'modelVariant' with variants 'simple' and 'detailed'*
>
> *2. shot.usda --- contains: Default prim /Shot, sublayers assets.usda, /Shot/Set/ChairA and ChairB as references to /Assets/Chair with different transforms, and /Shot/Lighting with a 'lightingVariant' containing 'day' (DistantLight) and 'night' (DomeLight) variants*

The model must produce a working Python script that, when executed, generates valid USD files. The validator then loads these files using the `pxr` library and runs 10 structural tests.

### 2.3 Skill Design and Injection

#### 2.3.1 Injection Mechanism

Skills are injected via the `.claude/skills/{name}/SKILL.md` path, which is the native skill discovery mechanism shared by all three supported CLIs. The workspace manager copies the skill file into the temporary workspace before the CLI starts, so the model discovers it through its normal skill-reading behavior. A **variant system** allows multiple formulations of the same skill to be tested: the format `domain:variant` resolves to `skills/{domain}/{variant}.md`, with `VARIANTS.yaml` declaring available variants and their metadata.

#### 2.3.2 Skill Design Philosophy

Skills were designed along a spectrum from broad reference to narrow task-specific, deliberately testing the hypothesis that skill granularity affects uplift:

**USD Composition Skills** (the primary experiment):

- **reference** (144 lines) --- A comprehensive API reference covering all USD composition patterns: sublayers, references, default prims, variant sets with `GetVariantEditContext()`, transforms, materials, lighting, and mesh definition. Designed to represent what a developer might paste from documentation. Includes 7 code sections covering patterns beyond what the task requires.

  *Design rationale:* Tests whether broad knowledge helps --- the "give them the docs" approach. Intentionally includes material binding and mesh patterns that the shot assembly task doesn't need, to test whether irrelevant context is harmful.

- **task-hints** (40 lines) --- A narrow, task-scoped skill containing only the APIs needed for the shot assembly task. Four code sections: stage/file setup, references, variant sets (with `GetVariantEditContext` highlighted as important), and lighting. No mesh definition, no materials, no transform details beyond `AddTranslateOp`.

  *Design rationale:* Tests whether minimal, targeted information outperforms comprehensive coverage. Created after the Phase 1 finding that broad skills harmed weaker models, as a manual attempt to reduce the "noise" that causes hallucination.

- **compiled-glm45** (80 lines, DSPy proxy-compiled) --- Automatically optimized by DSPy's BootstrapFewShot for glm-4.5-air-free using glm-5 as teacher. Contains the same patterns as task-hints but with slightly more detail and a full cube mesh example. Notably, the variant edit context section uses placeholder comments (`# configure mesh...`) rather than full code.

- **compiled-live-glm45** (59 lines, DSPy live-compiled) --- Optimized using actual benchmark runs in the loop (34 minutes, 6 iterations). The most concise compiled variant. The live metric ensures the skill actually helps the target model pass the task on Kilo.

- **compiled-qwen3-30b** (76 lines, DSPy proxy-compiled) --- Compiled specifically for qwen3-30b. Full working code examples inside variant contexts, including complete mesh point/face data. This is the most detailed compiled variant.

  *Design rationale:* Tests whether model-specific DSPy optimization produces better skills than cross-model transfer.

**Houdini Solaris Skills:**

- **SKILL (reference)** (160 lines) --- Complete Solaris reference covering `editableStage()`, prim definition (Xform, Mesh), transforms, lighting (Distant, Dome), materials (UsdPreviewSurface), material binding, and model kind. Includes a full "Complete Solaris Script Pattern" section showing all patterns composed together.

  *Design rationale:* Mirrors the USD reference approach for a second domain. Houdini Solaris is a more niche domain than USD, so models are expected to have weaker priors.

- **compiled-qwen3-30b** (74 lines, DSPy proxy-compiled) --- Numbered step-by-step matching the exact 10 requirements of the task. Each section contains the exact code pattern needed.

**General Domain Skills** (for tier 4 expansion tasks):

- **recursive-descent-parser** (102 lines) --- Provides the EBNF grammar, ASTNode structure, complete parser implementation using the tokenizer + recursive descent pattern, and evaluator. This is essentially a near-complete solution --- it tests whether giving the model a working reference implementation helps it produce correct code.

- **lru-cache-pattern** (70 lines) --- Provides the Node class, full LRUCache implementation with sentinel nodes, and key design points (no OrderedDict, sentinel head/tail, threading.Lock). Like the parser skill, this is close to a complete solution.

#### 2.3.3 Example: Skill Content Comparison

To illustrate how skill granularity works in practice, here is the critical "variant authoring" section from three USD skill variants:

**reference** (broad, 144 lines) --- 6 lines for variant sets:
```python
vset = prim.GetVariantSets().AddVariantSet("modelVariant")
vset.AddVariant("simple")
vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    geo = stage.DefinePrim("/Assets/Chair/Geo", "Mesh")
    # ... set mesh attributes
```

**task-hints** (narrow, 40 lines) --- 5 lines, labeled IMPORTANT:
```python
vset = prim.GetVariantSets().AddVariantSet("myVariant")
vset.AddVariant("optionA")
vset.SetVariantSelection("optionA")
with vset.GetVariantEditContext():
    child = stage.DefinePrim("/Parent/Child", "Xform")
```

**compiled-qwen3-30b** (DSPy, 76 lines) --- 18 lines with full mesh data inside variants:
```python
vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    mesh = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
    mesh.CreatePointsAttr([(-1,-1,-1), (1,-1,-1), ...])
    mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
    mesh.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, ...])
```

All three skills demonstrate the correct `GetVariantEditContext()` API. The difference is the level of surrounding detail, which proved to be the critical variable (Section 5.2).

### 2.4 DSPy Skill Compilation

To test automated skill optimization, we integrated DSPy's BootstrapFewShot optimizer. A teacher model (typically a stronger model) generates candidate skill documents, which are evaluated against either:

- **Proxy metric** --- a structural quality score assessing markdown formatting, code example presence, conciseness, and API pattern coverage (fast, no benchmark execution required)
- **Live metric** --- actual benchmark execution of the candidate skill against the target model on the target task (slow but behaviorally grounded)

The optimizer iterates, selecting the highest-scoring skill document.

### 2.5 Scoring and Validation

All scoring is automated via per-task `validate.py` scripts that assess functional correctness. Scores are continuous on a 0.0--1.0 scale, where 1.0 indicates full correctness and 0.0 indicates complete failure. An LLM-as-judge component exists in the framework but was not used in these experiments; all reported scores are from deterministic automated validation.

#### 2.5.1 Validation Methodology

Each validator follows a consistent pattern:

1. **Completion check** --- binary (0.0 or 1.0): does the expected output file exist?
2. **Execution** --- the generated code is actually run (via subprocess or in-process exec), not just statically analyzed
3. **Test suite** --- a set of structural and behavioral assertions against the execution output
4. **Score computation** --- `correctness = tests_passed / total_tests`

For the core USD shot assembly task, the validator runs 10 tests:

| # | Test | What It Checks |
|---|------|---------------|
| 1 | Default prim of assets.usda is `/Assets` | File structure |
| 2 | `/Assets/Chair` prim exists | Prim hierarchy |
| 3 | `modelVariant` set exists with `simple` and `detailed` | Variant mechanism |
| 4 | `/Assets/Chair/Geo` is a `UsdGeom.Mesh` | Geometry creation |
| 5 | Default prim of shot.usda is `/Shot` | Cross-file structure |
| 6 | `/Shot/Set/ChairA` exists (reference works) | Composition arc |
| 7 | `/Shot/Set/ChairB` exists (reference works) | Composition arc |
| 8 | ChairA and ChairB have different transforms | Transform ops |
| 9 | `lightingVariant` set has `day` and `night` | Variant mechanism |
| 10 | Variant switching produces different light types | Variant content |

A score of 0.9 means 9/10 tests passed --- for example, the variant sets exist but authoring content inside them failed. A score of 0.0 means the script either crashed, produced no files, or the files contained no valid USD structure.

For the Houdini Solaris task, the validator uses a **mock `hou` module** that provides a real `Usd.Stage` via `hou.pwd().editableStage()`, allowing the generated script to execute without a Houdini license. The mock captures the stage, and the validator inspects it for 10 required elements (scene hierarchy, mesh geometry with correct point counts, lighting, materials with shader binding, and model kind).

Pass threshold is `correctness >= 0.5` for tier 1 tasks and `correctness >= 0.7` for tier 3/4 tasks, reflecting the higher partial-credit granularity of domain tasks.

---

## 3. Experimental Setup

### 3.1 Models

Eight models were tested in Phase 2, all accessed via OpenRouter except Opus 4.6 on Claude Code (Anthropic subscription):

| Model | Parameters | Cost | Phase 2 Status |
|-------|-----------|------|----------------|
| claude-opus-4.6 | Unknown | Paid | Frontier ceiling reference |
| glm-5 | Unknown | Free | Top budget performer |
| qwen3-30b | 30B | Low | Strong mid-range |
| glm-4.5-air-free | Unknown | Free | Consistent moderate |
| qwen3-coder-next | Unknown | Free | Extreme CLI asymmetry |
| glm-4.7-flash | Unknown | Free | Low-mid performer |
| gemma-4-31b | 31B | Free | Inverse CLI asymmetry |
| minimax-m2.7 | Unknown | Free | Non-functional (0/66) |

Three additional models were tested in Phase 1 only: qwen3-coder-free and qwen3-next-80b-free (both timed out on every task, dropped for Phase 2).

### 3.2 CLI Environments

Two CLI environments were used:

- **Claude Code** --- Anthropic's official CLI, using `.env` file swapping for model selection. Injects additional context via hooks (superpowers SessionStart).
- **Kilo CLI** --- alternative CLI with Pyright LSP integration, provider-specific routing.

### 3.3 Task Inventory

The task set expanded from 2 (MVP) to 16 (Phase 1) to 33 (Phase 2) over the experimental period. The full inventory by tier:

| Tier | Task | Domain | Key Challenge | Timeout |
|------|------|--------|---------------|---------|
| 1 | hello-world | General | Baseline code execution | 120s |
| 1 | fizzbuzz | General | Basic logic | 120s |
| 2 | csv-pipeline | Data | File I/O, aggregation | 120s |
| 2 | cli-tool | CLI | argparse, multi-file handling | 120s |
| 2 | log-processor | Bash | POSIX text processing | 180s |
| 2 | makefile | Build | Automatic variables, phony targets | 180s |
| 2 | usd-scene | VFX | Basic USD prim/material creation | 120s |
| 2 | houdini-sop | VFX | Houdini SOP API (mock module) | 120s |
| 3 | expression-parser | CS | Recursive descent, operator precedence | 300s |
| 3 | lru-cache | CS | O(1) data structure, thread safety | 300s |
| 3 | git-hook | DevOps | Bash, git internals | 300s |
| 3 | service-generator | DevOps | systemd unit format | 300s |
| 3 | usd-shot-assembly | VFX | USD composition arcs, variant sets | 300s |
| 3 | houdini-solaris | VFX | Solaris LOPs, 10 USD operations | 300s |
| 4 | usd-shot-assembly (x5) | VFX | = tier 3 + skill variant | 300s |
| 4 | houdini-solaris (x2) | VFX | = tier 3 + skill variant | 300s |
| 4 | expression-parser | CS | = tier 3 + parser skill | 300s |
| 4 | lru-cache | CS | = tier 3 + cache skill | 300s |

The two primary experimental domains were chosen for their distance from typical training data:

- **USD (Pixar Universal Scene Description)** --- a niche Python API for 3D scene composition, used primarily in VFX pipelines. Models must understand composition arcs (sublayers, references), variant sets with the `GetVariantEditContext()` context manager, and transform operations. The specific challenge is `GetVariantEditContext()` --- models frequently hallucinate similar-sounding APIs (e.g., `LockVariant`, `.edit()`, `GetPrototypeStage`).
- **Houdini Solaris** --- an even more niche domain (SideFX's Solaris LOP system for USD scene layout). Tested via a mock `hou` module that provides a real `Usd.Stage` without requiring a Houdini license. Requires knowledge of 10 specific operations spanning geometry, lighting, materials, and model classification.

### 3.4 Skill Variants

Nine skill variants were tested across four domains, designed along a granularity spectrum (see Section 2.3.2 for design rationale):

| Variant | Lines | Method | Target | Proxy Score | Content Style |
|---------|-------|--------|--------|-------------|---------------|
| USD `reference` | 144 | Manual | General | N/A | Broad API docs, 7 sections, includes irrelevant patterns |
| USD `task-hints` | 40 | Manual | General | N/A | 4 sections, only task-relevant APIs, "IMPORTANT" labels |
| USD `compiled-glm45` | 80 | DSPy proxy | glm-4.5 | 0.80 | Moderate detail, placeholder comments in variant section |
| USD `compiled-live-glm45` | 59 | DSPy live | glm-4.5 | 1.00 | Most concise, behaviorally validated on Kilo |
| USD `compiled-qwen3-30b` | 76 | DSPy proxy | qwen3-30b | 1.00 | Full working code inside variants, highest detail |
| Solaris `SKILL` | 160 | Manual | General | N/A | Full Solaris reference with complete script pattern |
| Solaris `compiled-qwen3` | 74 | DSPy proxy | qwen3-30b | 0.84 | 9 numbered sections matching task requirements |
| `recursive-descent-parser` | 102 | Manual | General | N/A | EBNF grammar, complete parser + evaluator implementation |
| `lru-cache-pattern` | 70 | Manual | General | N/A | Node class, full LRUCache with sentinel nodes, key design points |

### 3.5 Experiment Timeline

| Date | Phase | Experiment | Runs |
|------|-------|-----------|------|
| Apr 3 | 1 | Framework development, early testing | 32 |
| Apr 4--5 | 1 | V1 Benchmark (5 models x 2 CLIs x 16 tasks) | 160 |
| Apr 6 | 1 | Skill variant experiment + Qwen3-30b experiment | 76 |
| Apr 6 | -- | **CHECKPOINT: archived 268 Phase 1 results** | -- |
| Apr 6--7 | 2 | **Clean benchmark (8 models x 33 tasks x 2 CLIs)** | **478** |
| | | **Grand total** | **746** |

---

## 4. Results

### 4.1 Phase 2: The Definitive Benchmark (478 runs)

Phase 2 ran 8 models across 2 CLIs on 33 tasks, producing 478 result files from a clean baseline with no carryover from Phase 1 exploration.

#### 4.1.1 Model Rankings

| Model | Overall Pass Rate | CC Passes | Kilo Passes |
|-------|-------------------|-----------|-------------|
| opus-4.6 (ceiling) | 62% | 10/10 | 0/6 (OpenRouter errors) |
| glm-5 | **61%** | 25/33 | 15/33 |
| qwen3-30b | 44% | 18/33 | 11/33 |
| glm-4.5-air-free | 39% | 13/33 | 13/33 |
| qwen3-coder-next | 32% | 21/33 | **0/33** |
| glm-4.7-flash | 30% | 9/33 | 11/33 |
| gemma-4-31b | 11% | **0/33** | 7/33 |
| minimax-m2.7 | 0% | 0/33 | 0/33 |

glm-5 is the clear top budget performer at 61%, approaching the Opus 4.6 ceiling of 62% (though the ceiling measurement is incomplete due to OpenRouter routing errors on Kilo). minimax-m2.7 produced zero passes across 66 runs and should be treated as non-functional for analysis purposes.

#### 4.1.2 Tier Calibration

| Tier | Pass Rate | Description |
|------|-----------|-------------|
| 1 | 60% | Baseline (hello-world, fizzbuzz) |
| 2 | 54% | General coding |
| 3 | 41% | Domain-specific, no skill |
| 4 | 18% | Domain-specific, with skill |

The progressive difficulty drop confirms the tier system's design. The drop from tier 3 (41%) to tier 4 (18%) remains counterintuitive --- tier 4 tasks include a skill that should theoretically help. This aggregate result, reproduced from Phase 1's similar pattern (92%, 78%, 42%, 25%), confirms that skills are net-negative at the population level.

The lower absolute pass rates compared to Phase 1 (e.g., T1 dropping from 92% to 60%) reflect the expanded model set: Phase 2 includes weaker models (minimax-m2.7 at 0%, gemma-4-31b at 11%) that were not present in Phase 1's GLM-only functional set.

#### 4.1.3 The CLI Environment as Dominant Variable

The most significant Phase 2 finding is the CLI environment's role as the dominant variable for skill effectiveness. Across 266 paired tier 3-vs-tier 4 comparisons:

| CLI | Mean Uplift | Positive | Neutral | Negative |
|-----|-------------|----------|---------|----------|
| Claude Code | **+0.147** | 40 (30%) | 84 (63%) | 9 (7%) |
| Kilo | **-0.068** | 9 (7%) | 95 (71%) | 29 (22%) |
| **Overall** | **+0.039** | 49 (18%) | 179 (67%) | 38 (14%) |

On Claude Code, skills produce a 4:1 ratio of positive-to-negative outcomes. On Kilo, the ratio inverts to roughly 1:3. The overall mean of +0.039 masks this CLI-dependent polarity entirely --- the aggregate number is meaningless without CLI stratification.

#### 4.1.4 Model-CLI Coupling Asymmetries

Phase 2 revealed extreme and previously unknown model-CLI coupling:

- **qwen3-coder-next**: 21/33 (64%) on Claude Code, **0/33 (0%)** on Kilo. The model is a strong mid-tier performer on one CLI and completely non-functional on the other.
- **gemma-4-31b**: **0/33 (0%)** on Claude Code, 7/33 (21%) on Kilo. The inverse pattern --- this model only works through Kilo.

These are not marginal differences. Two models with non-trivial capability are each locked to a single CLI, with the other CLI producing total failure. This asymmetry is independent of skill injection --- it applies to all tiers including tier 1 baseline tasks.

**glm-4.5-air-free** is the only model that showed perfect CLI parity: 13/33 on both Claude Code and Kilo.

### 4.2 Skill Uplift by Task Domain

#### 4.2.1 Houdini Solaris: The Clearest Positive Signal

The Houdini Solaris reference skill produced the most consistent positive uplift in the entire study. Three models went from 0.0 to 1.0 on Claude Code:

| Model | Tier 3 (no skill) CC | Tier 4 (with skill) CC | Uplift | Kilo Uplift |
|-------|----------------------|------------------------|--------|-------------|
| glm-5 | 0.0 | 1.0 | **+1.0** | 0.0 |
| qwen3-30b | 0.0 | 1.0 | **+1.0** | 0.0 |
| qwen3-coder-next | 0.0 | 1.0 | **+1.0** | 0.0 |

All three models are "at threshold" for this task --- they cannot solve it unaided but can synthesize from the skill document. On Kilo, the same skill with the same models produced zero improvement across all configurations. The domain is niche enough (Houdini Solaris scripting) that training data coverage is minimal, making the skill genuinely additive for capable models on a CLI that facilitates skill integration.

#### 4.2.2 Expression Parser: Extreme Polarization

The recursive-descent-parser skill (102 lines, near-complete solution) shows the most extreme polarization of any skill in the study:

| Model | CLI | Tier 3 | Tier 4 | Uplift |
|-------|-----|--------|--------|--------|
| glm-5 | CC | 0.0 | 1.0 | **+1.0** |
| glm-4.5-air-free | CC | 0.1 | 1.0 | **+0.9** |
| glm-4.7-flash | CC | 1.0 | 0.0 | **-1.0** |
| glm-5 | Kilo | 1.0 | 0.0 | **-1.0** |

The same skill, same model (glm-5), produces +1.0 on Claude Code and -1.0 on Kilo. glm-4.7-flash can solve the task on Claude Code without the skill (1.0) but the skill destroys its correct approach (-1.0). This near-complete-solution skill is maximally helpful for models that need it and maximally destructive for models that already have the answer, with the CLI determining which category a given model falls into.

#### 4.2.3 LRU Cache: Mostly Neutral

The lru-cache-pattern skill (70 lines, near-complete solution) showed minimal effect:

- Most models that can solve the task already score 1.0 without the skill
- Two small positives on Kilo: glm-4.5 0.0 to 0.5 (+0.5), glm-4.7 0.7 to 1.0 (+0.3)
- The task appears sufficiently well-represented in training data that skills provide little additive value

This contrasts sharply with the niche USD and Houdini domains, suggesting that skill uplift potential correlates with domain rarity in training data.

#### 4.2.4 USD Shot Assembly: High Variance, CLI-Dependent

The USD shot assembly task remains the most thoroughly tested domain (5 skill variants), but Phase 2 introduced a critical finding: **qwen3-30b scored 0.0 on the no-skill tier 3 version**, despite scoring 1.0 on the identical task in Phase 1. This run-to-run variance (Section 4.3) means that the Phase 1 conclusion --- that qwen3-30b was "above the capability threshold" for USD tasks --- may have been based on a lucky run.

### 4.3 Run-to-Run Variance

Phase 2 confirmed the high variance first observed in Phase 1 (entry #037). The most striking example:

- **qwen3-30b on tier3-usd-shot-assembly (Claude Code)**: scored 1.0 in Phase 1, scored 0.0 in Phase 2. Same task, same model, same CLI, same configuration. The only difference is the run itself.

This variance is not limited to domain-specific tasks. It represents a fundamental challenge for single-run benchmarking: any individual data point may not be representative. Our Phase 2 dataset uses single runs per configuration, which means individual scores should be interpreted as samples from a distribution rather than deterministic measurements.

### 4.4 Phase 1 Findings (Archived, 268 runs)

Phase 1 established the foundational hypotheses that Phase 2 tested at scale. Key findings that informed Phase 2 design:

1. **Capability threshold theory** (confirmed in Phase 2): Skills only help models near a task-specific capability threshold. glm-4.5's score dropped from 0.8 to 0.2 when given the broad USD skill (below threshold, hallucination amplification), while glm-5 went from 0.0 to 1.0 on Houdini Solaris (at threshold, genuine uplift).

2. **Skill detail paradox** (confirmed): More detailed skills cause more harm. The `compiled-glm45` variant (vague, placeholder comments) scored 0.9 for qwen3-30b on USD, while `compiled-qwen3-30b` (detailed, full code) scored 0.0. Vague skills let models route around complexity; detailed skills encourage hallucinated imitation.

3. **Cross-model transfer** (confirmed): Skills compiled for a different model (`compiled-glm45`) outperformed skills compiled for the target model (`compiled-qwen3-30b`), scoring 0.9 vs 0.0 for qwen3-30b on Claude Code.

4. **Proxy metric failure** (confirmed): The `compiled-qwen3-30b` skill achieved the maximum DSPy proxy score of 1.00 but produced the minimum real score of 0.0. Structural quality does not predict behavioral compliance.

5. **CLI confound** (upgraded to primary finding in Phase 2): Phase 1 noted that same model-skill pairs produced opposite results on different CLIs. Phase 2 elevated this from "confounding variable" to "dominant variable" based on 266 paired comparisons.

---

## 5. Discussion

### 5.1 Revised Theory: CLI Determines Direction of Skill Effect

Phase 2 data supports a revised theoretical framework that supersedes the Phase 1 capability threshold model. The original theory posited three zones (below/at/above threshold) that predicted skill effectiveness based on model capability alone. Phase 2 retains this model-capability axis but adds the CLI environment as a second, dominant axis:

**The capability threshold determines susceptibility.** Models at the threshold for a given task are most susceptible to skill effects --- the skill can tip the balance in either direction. Models far below the threshold are largely unaffected (the task is impossible regardless). Models far above are also less susceptible (the model's strong priors resist skill influence, though interference is still possible).

**The CLI environment determines direction.** Claude Code's environment (hooks, context injection, CLAUDE.md integration) appears to amplify skill content constructively --- models integrate the skill's patterns into their approach. Kilo's environment (Pyright LSP feedback, AGENTS.md integration, provider routing) appears to amplify skill content destructively --- models fight against conflicting signals from the LSP and the skill.

This two-axis model explains the full Phase 2 dataset:
- Houdini Solaris +1.0 on CC, 0 on Kilo: at-threshold models, CLI determines sign
- Expression parser +1.0 for glm-5 on CC, -1.0 for glm-5 on Kilo: same model, same skill, CLI flips the sign
- LRU cache neutral everywhere: above-threshold task (well-known domain), low susceptibility regardless of CLI
- Model-CLI coupling (qwen3-coder-next 64%/0%, gemma-4-31b 0%/21%): CLI determines baseline capability before skills are even introduced

### 5.2 The Skill Detail Paradox (Confirmed)

Phase 2 reinforces the Phase 1 finding that **more correct and detailed skill content can produce worse outcomes**. This paradox arises because detailed skills encourage models to attempt complex operations they then hallucinate, while vague skills allow models to route around complexity using their own (potentially simpler but correct) approaches. The implication is that skill authoring should optimize for minimum viable information, not comprehensiveness.

### 5.3 Proxy Metric Limitations (Confirmed)

The DSPy proxy metric --- optimizing for structural quality (markdown formatting, code examples, conciseness, API pattern coverage) --- proved not predictive of real-world performance. The `compiled-qwen3-30b` skill achieved the maximum proxy score of 1.00 but produced the minimum real score of 0.0. Structural quality and behavioral compliance are orthogonal dimensions. Live-metric compilation, which uses actual benchmark execution in the optimization loop, produced more reliable results but at substantially higher cost (34 minutes vs seconds for proxy evaluation) and is inherently CLI-specific --- further reinforcing the CLI-as-dominant-variable finding.

### 5.4 Domain Rarity and Skill Potential

Phase 2's addition of two general-domain skills (expression parser, LRU cache) alongside two niche-domain skills (USD composition, Houdini Solaris) reveals a pattern: **skill uplift potential correlates with domain rarity in training data**.

- **Houdini Solaris** (most niche): strongest and most consistent positive uplift on the facilitative CLI
- **USD composition** (niche): moderate, variable uplift
- **Expression parser** (intermediate): polarized, depends heavily on whether model already knows the pattern
- **LRU cache** (common): mostly neutral, models either already know it or cannot benefit from being told

This suggests skills are most valuable precisely where models need them most --- in domains with minimal training data coverage --- but only when delivered through a CLI environment that facilitates constructive integration.

### 5.5 Threats to Validity

This study has several significant limitations:

1. **Single-run variance.** Most configurations were tested with a single run. qwen3-30b scored 1.0 in Phase 1 and 0.0 in Phase 2 on the same task, meaning individual data points may not be representative. Statistical significance testing requires multiple runs per configuration, which resource constraints prevented.

2. **Model set composition.** While expanded from 4 (Phase 1) to 8 (Phase 2), the model set is dominated by free-tier models with unknown parameter counts and training data. The capability threshold theory requires validation across a more controlled range of model sizes.

3. **CLI confound.** The inability to isolate CLI effects from skill effects means that some observed "skill harm" may actually be "CLI harm amplified by skill presence." The two CLIs differ in multiple dimensions simultaneously (LSP, context injection, provider routing, hook system), preventing attribution to any single mechanism.

4. **Domain specificity.** The strongest uplift signals come from the most niche domains (Houdini Solaris, USD composition). Results may not generalize to more common programming domains where models have stronger priors.

5. **Automated scoring only.** While deterministic, the `validate.py` scripts assess functional correctness against specific test cases. They do not capture code quality, maintainability, or partial understanding that an LLM judge might identify.

6. **Frontier ceiling incomplete.** Opus 4.6 was only run on 10 CC tasks and 6 Kilo tasks (with OpenRouter errors), so the ceiling measurement is partial. A complete frontier reference across all 33 tasks on both CLIs would strengthen the analysis.

7. **Non-functional models.** minimax-m2.7 (0/66) contributes noise to aggregate statistics. Some analyses exclude it, but its inclusion in the 478-run count should be noted.

---

## 6. Conclusion

### 6.1 Summary of Contributions

This study makes five contributions based on 746 runs across two experimental phases:

1. **CLI environment as dominant variable** --- We demonstrate across 266 paired comparisons that the CLI environment, not skill content or model capability, is the primary determinant of whether skills help or harm. Claude Code produces a mean uplift of +0.147; Kilo produces -0.068 with the same skills and models. This is the central finding of Phase 2 and the most important revision to Phase 1's capability-threshold-centric theory.

2. **The capability threshold model (confirmed and refined)** --- We confirm that skill uplift follows a non-monotonic pattern with respect to model capability: skills help only models near a narrow capability threshold and are neutral or harmful for models above or below it. Phase 2 refines this by showing that the threshold determines *susceptibility* to skill effects, while the CLI determines the *direction*.

3. **The skill detail paradox (confirmed)** --- We confirm across both phases that more detailed and correct skill content can produce worse outcomes than vague or incomplete skills, because detailed content encourages models to attempt operations they then hallucinate.

4. **Model-CLI coupling asymmetries** --- We document extreme cases where capable models are entirely locked to a single CLI (qwen3-coder-next: 64% CC / 0% Kilo; gemma-4-31b: 0% CC / 21% Kilo), demonstrating that the CLI is not merely a confound for skill measurement but a fundamental determinant of model functionality.

5. **Domain rarity correlation** --- We show that skill uplift potential correlates with domain rarity in training data: niche domains (Houdini Solaris) show the strongest positive uplift on facilitative CLIs, while well-known domains (LRU cache) show minimal skill effect regardless of CLI.

### 6.2 Implications for Practitioners

The primary practical implication is clear: **do not blindly inject domain knowledge into LLM coding workflows**. Specifically:

- Before adding skills, establish a no-skill baseline. If the model already solves the task reliably, adding skills will likely hurt.
- Prefer narrow, task-scoped skills over broad reference documents. Minimum viable information outperforms comprehensive coverage.
- **Test skills against the specific CLI environment in which they will be deployed.** This is not optional guidance --- it is the single most important factor. A skill that helps on Claude Code may actively harm on Kilo, and vice versa.
- Do not trust proxy metrics for skill quality. Only live evaluation against the target model on the target task, on the target CLI, provides reliable signal.
- Focus skill investment on niche domains where models have weak priors. For well-known programming patterns, skills add little value.
- Be aware of model-CLI coupling: your model selection and CLI selection are not independent decisions.

### 6.3 Future Work

Several directions emerge from this study:

1. **Multi-run statistical validation** --- Repeat key experiments with 5--10 runs per configuration to establish confidence intervals and statistical significance. The qwen3-30b 1.0/0.0 variance on the same task demands this.
2. **CLI ablation study** --- Systematically disable CLI features (LSP feedback, hook injection, context files) to isolate which mechanisms drive the CLI direction effect.
3. **Adaptive skill injection** --- Develop a predictor that estimates whether a model is at the capability threshold for a given task, and whether the current CLI facilitates constructive skill integration, before deciding whether to inject a skill.
4. **Broader model range** --- Test across a controlled range of model sizes within a single family (e.g., Qwen 7B, 14B, 32B, 72B) to map the capability threshold more precisely.
5. **Broader domains** --- Extend to more common programming domains (web development, data science) where models have stronger priors and the threshold dynamics may differ.
6. **Skill titration** --- Systematically vary skill detail level to map the relationship between information density and uplift across the capability spectrum.
7. **Cross-phase replication** --- Re-run the exact Phase 1 configurations to quantify run-to-run variance at scale rather than relying on incidental cross-phase observations.

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

### A.3 General Domain Skills

| Skill | Lines | Method | Key Property |
|-------|-------|--------|--------------|
| `recursive-descent-parser` | 102 | Manual | EBNF grammar, complete parser + evaluator implementation |
| `lru-cache-pattern` | 70 | Manual | Node class, full LRUCache with sentinel nodes, key design points |

### A.4 Phase 2 Skill Uplift Summary: Claude Code vs Kilo

| Task Domain | CC Positive | CC Negative | Kilo Positive | Kilo Negative | Key Pattern |
|-------------|-------------|-------------|---------------|---------------|-------------|
| Houdini Solaris | 3 models +1.0 | 0 | 0 | 0 | Strongest positive signal, CC-only |
| Expression Parser | 2 models (+1.0, +0.9) | 1 model (-1.0) | 0 | 1 model (-1.0) | Extreme polarization |
| USD Shot Assembly | Variable | Variable | Rare | Common | High variance, CLI-dependent |
| LRU Cache | Minimal | Minimal | 2 small positives | Minimal | Neutral (well-known domain) |

## Appendix B: Log Entry Index

| Entry | Date | Phase | Category | Title |
|-------|------|-------|----------|-------|
| #001 | 2026-04-03 | 1 | Method | Framework design --- 4-tier task system |
| #002 | 2026-04-03 | 1 | Method | Skill injection via .claude/skills/ |
| #003 | 2026-04-03 | 1 | Context | Core research question defined |
| #003b | 2026-04-03 | 1 | Method | Domain selection --- USD and Houdini |
| #003c | 2026-04-03 | 1 | Method | Validation approach --- execution-based scoring |
| #003d | 2026-04-05 | 1 | Method | Skill design spectrum |
| #004 | 2026-04-03 | 1 | Context | MVP framework implemented |
| #005 | 2026-04-03 | 1 | Result | Early dev runs (32 runs) |
| #006 | 2026-04-04 | 1 | Method | Selected 5 free/cheap OpenRouter models |
| #007 | 2026-04-04 | 1 | Finding | 2 of 5 free models non-functional |
| #008 | 2026-04-05 | 1 | Method | Expanded to 16 tasks |
| #009 | 2026-04-05 | 1 | Result | V1 Benchmark --- 160 runs, 6.3 hours |
| #010 | 2026-04-05 | 1 | Finding | Tier difficulty calibrated: 92/78/42/25% |
| #011 | 2026-04-05 | 1 | Surprise | Broad skill destroys glm-4.5 (0.8 to 0.2) |
| #012 | 2026-04-05 | 1 | Finding | Root cause: hallucination amplification |
| #013 | 2026-04-05 | 1 | Hypothesis | Capability threshold theory |
| #014 | 2026-04-05 | 1 | Surprise | glm-5 + houdini skill: 0.0 to 1.0 |
| #015 | 2026-04-05 | 1 | Method | Skill variant system |
| #016 | 2026-04-05 | 1 | Method | Task-hints variant (40 lines) |
| #017 | 2026-04-05 | 1 | Method | DSPy skill compiler |
| #018 | 2026-04-06 | 1 | Result | DSPy proxy compilation for glm-4.5 |
| #019 | 2026-04-06 | 1 | Result | Variant experiment --- all net-negative |
| #020 | 2026-04-06 | 1 | Surprise | Same model+skill opposite on different CLIs |
| #021 | 2026-04-06 | 1 | Finding | CLI confound root causes |
| #022 | 2026-04-06 | 1 | Finding | Benchmark measures CLI tooling too |
| #023 | 2026-04-06 | 1 | Result | DSPy live-metric compilation (34 min) |
| #024 | 2026-04-06 | 1 | Result | 18 variant runs --- 5 variants benchmarked |
| #025 | 2026-04-06 | 1 | Finding | No single variant works across CLIs |
| #026 | 2026-04-06 | 1 | Result | Qwen3-30b baseline benchmarks (12 runs) |
| #027 | 2026-04-06 | 1 | Result | DSPy compilation targeting qwen3-30b |
| #028 | 2026-04-06 | 1 | Result | Compiled variant benchmarks --- 0/4 pass |
| #029 | 2026-04-06 | 1 | Surprise | qwen3-30b: 1.0 without, 0.0 with own skill |
| #030 | 2026-04-06 | 1 | Finding | Hallucinated LockVariant() despite skill |
| #031 | 2026-04-06 | 1 | Finding | Skill detail paradox |
| #032 | 2026-04-06 | 1 | Finding | Cross-model transfer outperforms specific |
| #033 | 2026-04-06 | 1 | Finding | DSPy proxy metric not predictive |
| #034 | 2026-04-06 | 1 | Hypothesis | Skill harm zones refined |
| #035 | 2026-04-06 | 1 | Finding | Kilo 0.0 on all for qwen3-30b |
| #036 | 2026-04-06 | 1 | Finding | Houdini Solaris above difficulty ceiling |
| #037 | 2026-04-06 | 1 | Finding | Run-to-run variance is high |
| #038 | 2026-04-06 | -- | Method | **CHECKPOINT --- Phase 2 begins** |
| #039 | 2026-04-06 | 2 | Context | Phase 2 model lineup --- 8 models |
| #040 | 2026-04-07 | 2 | Result | Phase 2 complete --- 478 runs |
| #041 | 2026-04-07 | 2 | Finding | Skills help on CC (+0.147) but hurt on Kilo (-0.068) |
| #042 | 2026-04-07 | 2 | Finding | Houdini Solaris: +1.0 for 3 models on CC |
| #043 | 2026-04-07 | 2 | Surprise | Expression parser: extreme +/-1.0 swings |
| #044 | 2026-04-07 | 2 | Surprise | qwen3-30b 0.0 vs Phase 1's 1.0 --- variance confirmed |
| #045 | 2026-04-07 | 2 | Surprise | qwen3-coder-next: 21/33 CC, 0/33 Kilo |
| #046 | 2026-04-07 | 2 | Finding | minimax-m2.7 confirmed non-functional |
| #047 | 2026-04-07 | 2 | Finding | LRU cache skill has minimal effect |
| #048 | 2026-04-07 | 2 | Hypothesis | Revised theory: CLI determines direction |
