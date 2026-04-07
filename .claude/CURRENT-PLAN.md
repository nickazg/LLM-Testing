# Plan: Skill Taxonomy & Test Matrix Expansion — COMPLETED

## Context

The current benchmark conflates two fundamentally different types of skill uplift into a single measurement. The houdini-solaris and usd-composition skills provide **genuinely novel information** that budget models lack, while lru-cache-pattern and expression-parser skills provide **structured guidance on things models already know**. These measure different things but get reported as one "skill uplift" number.

Additionally, there's no coverage at all for **Domain Context** skills — org-specific conventions applied to known tech — which is arguably the most common real-world enterprise skill use case.

This plan introduces a three-category skill taxonomy, adds light/heavy intensity variants, expands VFX task coverage across 9 new tasks, and updates the codebase to support the new metadata.

## Skill Taxonomy

| Category | What the model knows | What the skill provides | Classified by |
|----------|---------------------|------------------------|---------------|
| **Novel Knowledge** | Nothing about this API/tech | The API itself | Intent |
| **Workflow/Process** | The tech and how to use it | Structure, sequence, guardrails | Intent |
| **Domain Context** | The general tech | Org-specific conventions/constraints | Intent |

Model-relative effect (e.g., "Novel for Qwen, Workflow for Opus") tracked as secondary analysis dimension.

Each category has two intensities:
- **Heavy** — comprehensive reference / full conventions / prescriptive recipe
- **Light** — key patterns + gotchas / top 3 rules / approach + guardrails only

---

## Phase 1: Schema & Codebase Changes

### 1.1 Update TaskConfig dataclass
**File:** `src/llm_bench/models.py` (lines 40-82)

Add fields to TaskConfig:
```python
difficulty: Optional[int] = None        # 1-5 scale
skill_type: Optional[str] = None        # "novel" | "workflow" | "context"
skill_intensity: Optional[str] = None   # "light" | "heavy"
skill_pair: Optional[str] = None        # links to baseline task name
```

Update `from_dir()` to read these from yaml.

### 1.2 Update RunResult dataclass
**File:** `src/llm_bench/models.py` (lines 100-111)

Add same 4 fields so results carry the metadata through to analysis.

### 1.3 Update runner to populate new fields
**File:** `src/llm_bench/runner.py` (lines 156-167)

Pass `skill_type`, `skill_intensity`, `skill_pair`, `difficulty` from TaskConfig to RunResult.

### 1.4 Update task loader with new filters
**File:** `src/llm_bench/loader.py` (lines 5-25)

Add optional `skill_types` and `difficulties` filter parameters to `load_tasks()`.

### 1.5 Update CLI with new filter args
**File:** `src/llm_bench/cli.py` (lines 30-35, 78-91, 215-234)

Add `--skill-types` and `--difficulties` CLI args. Update info display to show new fields.

### 1.6 Update dashboard
**File:** `src/llm_bench/dashboard/app.py`

- Add skill_type/intensity/difficulty to summary endpoint
- Add filter dropdowns in runs view
- Add columns to run table
- Update uplift view to group by skill_type

---

## Phase 2: Reclassify Existing Tasks

Update existing task.yaml files with new metadata fields:

| Task | difficulty | skill_type | skill_intensity | skill_pair |
|------|-----------|------------|-----------------|------------|
| hello-world | 1 | — | — | — |
| fizzbuzz | 1 | — | — | — |
| makefile | 2 | — | — | — |
| csv-pipeline | 2 | — | — | — |
| cli-tool | 2 | — | — | — |
| log-processor | 2 | — | — | — |
| usd-scene | 2 | — | — | — |
| houdini-sop | 2 | — | — | — |
| lru-cache (T3) | 3 | — | — | — |
| expression-parser (T3) | 3 | — | — | — |
| git-hook (T3) | 3 | — | — | — |
| service-generator (T3) | 3 | — | — | — |
| usd-shot-assembly (T3) | 3 | — | — | — |
| houdini-solaris (T3) | 3 | — | — | — |
| lru-cache (T4) | 3 | workflow | heavy | lru-cache |
| expression-parser (T4) | 3 | workflow | heavy | expression-parser |
| usd-shot-assembly (T4) | 3 | novel | heavy | usd-shot-assembly |
| houdini-solaris (T4) | 3 | novel | heavy | houdini-solaris |

Existing compiled variants also get tagged as `novel / heavy`.

---

## Phase 3: New Workflow/Light Skills (2 new skills)

### 3.1 lru-cache-workflow-light
**Create:** `skills/lru-cache-workflow-light/SKILL.md`

Content: approach + guardrails only. No implementation recipe.
- Use O(1) data structures for both get and put
- Thread safety is required — consider race conditions on eviction
- Watch for: duplicate key overwrites (update value AND move to front), capacity=0 edge case, eviction order (least recently used, not least frequently used)
- Test concurrent access — interleaved get/put sequences
- Don't use OrderedDict — the constraint is dict + linked list

**Create task:** `tasks/tier4/lru-cache-workflow-light/task.yaml`
- Same prompt as tier3-lru-cache
- skill: lru-cache-workflow-light
- skill_type: workflow, skill_intensity: light, skill_pair: lru-cache

### 3.2 expression-parser-workflow-light
**Create:** `skills/expression-parser-workflow-light/SKILL.md`

Content: approach + guardrails only.
- Use recursive descent with operator precedence levels
- Tokenize first, then parse, then evaluate — don't combine steps
- Precedence: +/- lowest, then *// higher, then unary minus, then parentheses
- Watch for: unary minus vs subtraction ambiguity, nested parentheses, empty input
- Error handling: ValueError for malformed expressions, ZeroDivisionError for division by zero
- Return floats, not ints — even for whole number results

**Create task:** `tasks/tier4/expression-parser-workflow-light/task.yaml`
- Same prompt as tier3-expression-parser
- skill: expression-parser-workflow-light
- skill_type: workflow, skill_intensity: light, skill_pair: expression-parser

---

## Phase 4: New Domain Context Skills (4 new skills)

### 4.1 git-hook-context-heavy
**Create:** `skills/git-hook-context-heavy/SKILL.md`

Our repository conventions:
- Max file size: 2MB (not generic 5MB)
- Python linting: must pass `ruff check --select=E,F,W`
- Commit message format: `^(feat|fix|chore|docs|refactor): [A-Z].+`
- Forbidden files: `.env`, `.credentials`, `*.pem`, `*.key` — hard block
- Staged binary files must live under `assets/bin/` with matching `.meta` file
- No `import *` in Python files

**Create task:** `tasks/tier4/git-hook-context-heavy/task.yaml`
- Prompt: same as tier3 BUT adds "follow our internal repository conventions as documented in your skills"
- skill_type: context, skill_intensity: heavy, skill_pair: git-hook

### 4.2 git-hook-context-light
**Create:** `skills/git-hook-context-light/SKILL.md`

Top 3 rules only:
- Commit messages must match `^(feat|fix|chore|docs|refactor): [A-Z].+`
- No `.env` or credential files ever
- Python must pass `ruff check`

**Create task:** `tasks/tier4/git-hook-context-light/task.yaml`
- skill_type: context, skill_intensity: light, skill_pair: git-hook

### 4.3 service-generator-context-heavy
**Create:** `skills/service-generator-context-heavy/SKILL.md`

Our infrastructure conventions:
- Service user: `svc-{name}`, never root
- Logs to `/var/log/platform/{name}/`
- Required dependencies: `consul-agent.service`, `vault-agent.service`
- `LimitNOFILE=65535` and `LimitNPROC=4096` mandatory
- Env vars from `/etc/platform/{name}/env`
- Working dir: `/opt/platform/{name}/`
- Restart: always `on-failure` with `RestartSec=10`
- `WantedBy=multi-user.target`
- Health check: `ExecStartPre=/opt/platform/bin/healthcheck --service={name}`

**Create task:** `tasks/tier4/service-generator-context-heavy/task.yaml`
- Prompt: same as tier3 BUT adds "follow our internal infrastructure standards"
- skill_type: context, skill_intensity: heavy, skill_pair: service-generator

### 4.4 service-generator-context-light
**Create:** `skills/service-generator-context-light/SKILL.md`

Top 3 rules:
- Service user: `svc-{name}`, never root
- Depends on `consul-agent.service`
- Env from `/etc/platform/{name}/env`

**Create task:** `tasks/tier4/service-generator-context-light/task.yaml`
- skill_type: context, skill_intensity: light, skill_pair: service-generator

---

## Phase 5: New VFX Baseline Tasks (9 new tasks)

Each needs: task.yaml, template/ dir (if needed), validate.py.

### 5.1 USD Render Settings (difficulty: 3)
**Dir:** `tasks/tier3/usd-render-settings/`

Prompt: Create render pipeline config — UsdRender.Product for output image, UsdRender.Var for AOVs (beauty, depth, normal), UsdGeom.Camera with focal length/aperture, render settings prim with resolution and pixel aspect ratio. Multi-file: camera rig in one file, render config referencing it in another.

Subsystem tested: UsdRender, cameras, render pipeline configuration.

### 5.2 USD Procedural Animation (difficulty: 3)
**Dir:** `tasks/tier3/usd-procedural-animation/`

Prompt: Create skeletal animation — UsdSkel.Root, UsdSkel.Skeleton with joint hierarchy, UsdSkel.Animation with time-sampled joint transforms over frame range, bind mesh to skeleton with joint weights.

Subsystem tested: UsdSkel, time samples, deformation binding.

### 5.3 USD Stage Layers & Opinions (difficulty: 3)
**Dir:** `tasks/tier3/usd-stage-layers/`

Prompt: Create multi-layer editorial — base layer with character, stronger animation layer overriding transforms with time samples, third layer adding material override. Manage layer stack ordering, use Sdf.Layer API, demonstrate opinion resolution.

Subsystem tested: Sdf.Layer, layer stack ordering, opinion strength, composed vs uncomposed queries.

### 5.4 USD Shader Graph (difficulty: 3)
**Dir:** `tasks/tier3/usd-shader-graph/`

Prompt: Create multi-material shader network — UsdShade.NodeGraph with connected nodes, UsdPreviewSurface with UsdUVTexture + UsdPrimvarReader_float2, second material blending textures, wire with ConnectToSource, UsdGeom.Subset for per-face material assignment.

Subsystem tested: Shader graph connectivity, primvar readers, face-set material assignment.

### 5.5 USD Custom Schema & Metadata (difficulty: 3)
**Dir:** `tasks/tier3/usd-custom-schema/`

Prompt: Create prims with custom API schemas (ApplyAPI), custom properties with Sdf.ValueTypeNames, assetInfo dictionaries, custom metadata via SetCustomDataByKey, purpose (render/proxy/guide) for visibility control.

Subsystem tested: Custom properties, metadata, API schemas, asset resolution, purpose.

### 5.6 Houdini PDG/TOPs (difficulty: 3)
**Dir:** `tasks/tier3/houdini-pdg/`

Prompt: Create TOP network — Python Processor generating work items from file list, Partition by Attribute to group, Python Script to process each work item, Wait for All before summary node. Set attributes, manage work item dependencies.

Subsystem tested: PDG work items, processors, partitioners, attribute patterns.

### 5.7 Houdini Solaris Instancing (difficulty: 3)
**Dir:** `tasks/tier3/houdini-solaris-instancing/`

Prompt: Create Solaris LOP script — ground plane mesh, UsdGeom.PointInstancer with 3 prototype tree variants, set positions/protoIndices/orientations, add UsdCollection for vegetation light linking.

Subsystem tested: PointInstancer, prototype registration, per-instance attributes, collections.

### 5.8 Houdini Solaris Render & AOVs (difficulty: 3)
**Dir:** `tasks/tier3/houdini-solaris-render/`

Prompt: Create Solaris LOP script — RenderProduct with output path, RenderVar prims for AOVs (beauty/depth/cryptomatte), Karma renderer settings with sample counts/resolution, link to camera, render pass with light path expressions.

Subsystem tested: Render products, AOV definitions, Karma settings within LOPs.

### 5.9 Houdini Solaris Light Linking (difficulty: 3)
**Dir:** `tasks/tier3/houdini-solaris-light-linking/`

Prompt: Create Solaris LOP script — multiple lights (key/fill/rim), UsdCollections on each for include/exclude geometry, light filters (barn door/blocker) as child prims, purpose attributes (render/proxy/guide), categories for light linking.

Subsystem tested: Light linking, collections-based illumination, light filters, purpose-driven visibility.

---

## Phase 6: Novel Knowledge Skills for New VFX Tasks (18 new skills)

Each of the 9 new VFX baseline tasks gets a **novel-heavy** and **novel-light** skill variant.

For each task, create:
1. `skills/{task-name}/SKILL.md` — heavy (full API reference, ~100-150 lines)
2. `skills/{task-name}-light/SKILL.md` — light (key patterns + gotchas, ~20-30 lines)
3. Corresponding task.yaml in `tasks/tier4/` pointing to each skill

This requires **web research** into each API subsystem to write accurate skill content:
- UsdRender API
- UsdSkel API
- Sdf.Layer API
- UsdShade.NodeGraph / ConnectToSource API
- Custom API schemas / metadata API
- Houdini PDG Python API
- Houdini Solaris PointInstancer patterns
- Houdini Solaris Karma render settings
- Houdini Solaris light linking / collections

### Heavy vs Light distinction:
- **Heavy:** Complete API reference — all classes, methods, parameter types, code examples
- **Light:** 3-5 critical patterns, top gotchas, minimal code snippets — enough to point the model in the right direction but not enough to copy-paste a solution

---

## Phase 7: Validation Scripts for New Tasks

Each of the 9 new baseline tasks needs a `validate.py` that checks correctness.

Each of the Domain Context task variants needs a `validate.py` that specifically checks for the org conventions (e.g., does the git hook check for ruff, does the service file use `svc-{name}`).

---

## Phase 8: Update Existing Tests

**File:** `tests/`

Update existing unit tests to handle new TaskConfig/RunResult fields. Add tests for:
- New field parsing from task.yaml
- Filter by skill_type and difficulty in loader
- Backward compatibility (old task.yamls without new fields still load)

---

## Final Task/Skill Matrix

**Total baseline tasks:** 26 (8 existing T1/T2 + 6 existing T3 + 3 existing T3 without T4 pairs that now get pairs + 9 new VFX T3)

Wait — let me recount properly:

**Baselines (no skill):** 17 tasks
- T1: 2 (hello-world, fizzbuzz)
- T2: 6 (makefile, csv-pipeline, cli-tool, usd-scene, houdini-sop, log-processor)
- T3: 9 existing + new (lru-cache, expression-parser, git-hook, service-generator, usd-shot-assembly, houdini-solaris, usd-render-settings, usd-procedural-animation, usd-stage-layers, usd-shader-graph, usd-custom-schema, houdini-pdg, houdini-solaris-instancing, houdini-solaris-render, houdini-solaris-light-linking) = **15**
- **Total baselines: 23**

**Skill variants:** 
- Workflow heavy: 2 (lru-cache, expression-parser) — exist, reclassify
- Workflow light: 2 (lru-cache, expression-parser) — new
- Context heavy: 2 (git-hook, service-generator) — new
- Context light: 2 (git-hook, service-generator) — new
- Novel heavy: 11 (usd-shot-assembly, houdini-solaris + 9 new VFX) — 2 exist + 9 new
- Novel light: 11 (usd-shot-assembly, houdini-solaris + 9 new VFX) — all new
- **Total skill variants: 30**

**Grand total: 53 tasks** (23 baselines + 30 skill variants)
Plus existing compiled variants which carry over.

---

## Verification

1. **Schema changes:** Run `pytest tests/ -v` — all existing tests pass with new optional fields
2. **Reclassification:** Run `llm-bench info` — verify existing tasks show new metadata
3. **New task loading:** Run `llm-bench info --tiers 3` — verify 15 tier-3 tasks discovered
4. **Filter by type:** Run `llm-bench info --skill-types novel` — verify only novel tasks shown
5. **Skill injection:** Run a single task with a new skill variant, verify skill.md lands in workspace
6. **Domain Context validation:** Run git-hook-context-heavy, verify validate.py checks for org conventions
7. **End-to-end:** Run `llm-bench run --models qwen3-30b --clis kilo --tasks lru-cache,lru-cache-workflow-light,lru-cache-workflow-heavy` — verify three results with correct metadata, uplift calculable between them
8. **Dashboard:** Launch dashboard, verify new filter dropdowns and uplift grouped by skill_type

---

## Execution Order

Phases 1-2 first (schema + reclassify) — this is the foundation.
Phase 3-4 in parallel (workflow-light + context skills) — independent of each other.
Phase 5 next (new VFX baselines) — needs research per subsystem.
Phase 6 after 5 (novel skills for new tasks) — depends on task prompts being finalized.
Phase 7 after 5-6 (validation scripts).
Phase 8 throughout (tests updated incrementally).

---

## Execution Notes

### Completed
- [x] Phase 1: Schema changes (TaskConfig, RunResult, loader, CLI, dashboard)
- [x] Phase 2: Reclassified all 33 existing tasks with new metadata
- [x] Phase 3: Created 2 workflow/light skills (lru-cache, expression-parser)
- [x] Phase 4: Created 4 domain context skills (git-hook heavy/light, service-generator heavy/light) with custom validators
- [x] Phase 5: Created 9 new VFX baseline tasks (5 USD + 4 Houdini)
- [x] Phase 6: Created 24 novel knowledge skills (heavy + light for all 9 new + 2 existing VFX tasks) + 24 tier4 tasks
- [x] Phase 7: Validation scripts created alongside tasks
- [x] Phase 8: 6 new unit tests added (75 total, all passing)

### Final Counts
- 68 tasks total (was 33)
- 26 skill directories (was 4, not counting compiled variants)
- 75 tests passing (was 69)

### Notes for Developer
- Task naming: tier4 novel tasks use `-novel` and `-novel-light` suffixes to distinguish from future workflow/context variants
- Existing compiled variants (DSPy) all tagged as novel/heavy, carrying over unchanged
- Domain context validators are custom (check for org conventions), not copies of tier3
- Houdini validators use source code analysis (string matching) since hou module isn't available in test env
- USD validators try pxr import first, fall back to text-based checks
- No commits made — awaiting developer approval
