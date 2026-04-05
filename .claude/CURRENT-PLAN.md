# Plan: Real-World Benchmark Tasks & Skills

**STATUS: COMPLETE** — All 15 tasks + 2 skills implemented. 16 tasks loading, 54 tests passing.

## Context
The framework has 2 tier 1 tasks and no tier 2/3/4 tasks or skills. The user wants real-world tasks across 5 domains: Pixar USD, Houdini SideFX, generic Python, advanced Python, and CLI/Bash. These need to be heavily researched and based on actual use cases. Tier 3/4 pairs enable the skill uplift experiment (the project's core purpose).

---

## Task Inventory (15 tasks + 2 skills)

### Generic Python — Tier 2 (4 tasks)
| ID | Name | Key File | Validation |
|----|------|----------|------------|
| `tier2-csv-pipeline` | CSV Data Pipeline | `pipeline.py` | Run script, compare output.csv rows against expected |
| `tier2-cli-tool` | CLI Word Count Tool | `wordcount.py` | Run with flag combos, compare stdout to expected |
| `tier2-log-processor` | Bash Log Analyzer | `analyze.sh` | Run on synthetic access.log, check section outputs |
| `tier2-makefile` | Multi-target Makefile | `Makefile` | Parse targets, run `make -n`, check structure |

### Advanced Python — Tier 3 (2 tasks)
| ID | Name | Key File | Validation |
|----|------|----------|------------|
| `tier3-lru-cache` | LRU Cache (O(1), thread-safe) | `lru_cache.py` | Import class, run 15 test scenarios |
| `tier3-expression-parser` | Expression Parser + AST | `expr_parser.py` | Test 20 expressions, check AST shape |

### CLI/Bash — Tier 2-3 (2 tasks)
| ID | Name | Key File | Validation |
|----|------|----------|------------|
| `tier3-git-hook` | Git Pre-commit Hook | `pre-commit` | Create temp repo, stage bad files, verify rejection |
| `tier3-service-generator` | Systemd Unit Generator | `generate_service.py` | Run with args, parse INI output, verify fields |

### Pixar USD — Tier 2-4 (3 tasks, 1 skill)
| ID | Name | Key File | Validation |
|----|------|----------|------------|
| `tier2-usd-scene` | USD Scene with Materials | `build_scene.py` → `scene.usda` | Load with pxr, check prims/transforms/bindings |
| `tier3-usd-shot-assembly` | Shot Assembly + Variants | `assemble_shot.py` → `shot.usda` + `assets.usda` | Check composition arcs, variant switching, references |
| `tier4-usd-shot-assembly` | Same + skill | (identical to tier3) | skill: `usd-composition` |

### Houdini SideFX — Tier 2-4 (3 tasks, 1 skill)
| ID | Name | Key File | Validation |
|----|------|----------|------------|
| `tier2-houdini-sop` | SOP Network + HDA Parms | `build_sop_network.py` | Mock hou module tracks API calls |
| `tier3-houdini-solaris` | Solaris Python Script LOP | `solaris_lop.py` | Mock hou + real USD stage inspection |
| `tier4-houdini-solaris` | Same + skill | (identical to tier3) | skill: `houdini-solaris` |

---

## Implementation Order (8 steps)

### Step 1: Framework updates
- [ ] **`pyproject.toml`**: Add `usd = ["usd-core>=25.5"]` optional dep group
- [ ] **`runner.py`** line 16: Add `.usda: "usd"`, `.usdc: "usd"`, `.c: "c"`, `.h: "c"` to LANG_MAP
- [ ] Create directories: `tasks/tier2/`, `tasks/tier3/`, `tasks/tier4/`, `skills/`

### Step 2: Generic Python tier 2 tasks (easiest, establishes patterns)
1. - [ ] **`tier2-csv-pipeline`** — template has `input.csv` (20 rows: name,department,salary,status). Prompt: filter active, group by dept, compute avg salary, output `output.csv`. Validate by comparing rows.
2. - [ ] **`tier2-cli-tool`** — template has `sample1.txt`, `sample2.txt`. Prompt: argparse tool like `wc` with `--lines/--words/--chars`. Validate output format.

### Step 3: CLI/Bash tier 2 tasks
3. - [ ] **`tier2-log-processor`** — template has synthetic `access.log` (~100 lines). Prompt: top 5 IPs, status code counts, top 3 paths. Validate parsed sections.
4. - [ ] **`tier2-makefile`** — template has `src/main.c`, `src/utils.c`, `include/utils.h`. Prompt: Makefile with all/clean/test/install targets, auto variables, incremental builds. Validate target existence and `make -n` output.

### Step 4: Advanced Python tier 3 tasks
5. - [ ] **`tier3-lru-cache`** — from scratch. LRUCache class with O(1) get/put, no OrderedDict, thread-safe. Validate with 15 test scenarios including eviction, overwrites, threading.
6. - [ ] **`tier3-expression-parser`** — from scratch. parse() → ASTNode, evaluate() → float. Support +,-,*,/,unary-,parens. Validate 20 expressions + error cases.

### Step 5: CLI tier 3 tasks
7. - [ ] **`tier3-git-hook`** — from scratch. Pre-commit: reject >5MB files, print() debugging, trailing whitespace, py_compile. Validate by creating temp git repo with bad staged files.
8. - [ ] **`tier3-service-generator`** — from scratch. Python script that generates systemd unit files from CLI args. Validate parsed INI sections.

### Step 6: USD tasks + skill
9. - [ ] **`tier2-usd-scene`** — from scratch. Build scene.usda with hierarchy (/World/Ground, /Character, /Light), mesh, DomeLight, material binding. Validate with pxr: check prims, types, transforms, binding.
10. - [ ] **`tier3-usd-shot-assembly`** — from scratch. Create assets.usda + shot.usda with sublayers, references (2 chairs), variant set (day/night lighting). Validate: composition arcs, variant switching, transform overrides.
11. - [ ] **`tier4-usd-shot-assembly`** — EXACT copy of tier3, only `id`/`tier`/`skill` differ in task.yaml. Skill: `usd-composition`
12. - [ ] **Skill: `skills/usd-composition/SKILL.md`** — Reference covering: sublayer ordering, variant EditContext, xformOp patterns, material binding API, default prim, multi-file composition

### Step 7: Houdini tasks + skill + mock framework
13. - [ ] **Mock `hou` module** (~200 lines) — tracks createNode/setInput/parm.set calls, provides ParmTemplate classes. For Solaris: `hou.pwd().editableStage()` returns real `Usd.Stage.CreateInMemory()`.
14. - [ ] **`tier2-houdini-sop`** — template includes mock hou/. Prompt: create geo container, grid→mountain→color→null chain, set parms, build HDA ParmTemplateGroup. Validate recorded API calls.
15. - [ ] **`tier3-houdini-solaris`** — template includes Solaris-variant mock hou/. Prompt: Python Script LOP code that builds USD scene via hou.pwd().editableStage(). Validate the actual USD stage.
16. - [ ] **`tier4-houdini-solaris`** — EXACT copy of tier3. Skill: `houdini-solaris`
17. - [ ] **Skill: `skills/houdini-solaris/SKILL.md`** — Reference covering: editableStage() pattern, pxr imports, prim definition, material binding in Solaris, light creation, ModelAPI kind, default prim

### Step 8: Integration verification
- [ ] Run `llm-bench info` — verify all 15 tasks and 2 skills show up
- [ ] Run each validate.py against its own template (should score 0.0 — no solution present)
- [ ] Verify tier 3/4 pairs are identical except yaml fields
- [ ] Run `pytest tests/ -v` — existing tests still pass

---

## File Counts
- **Tasks**: 15 directories, ~52 files total
- **Skills**: 2 directories, 2 SKILL.md files
- **Framework changes**: 2 files (pyproject.toml, runner.py)
- **Mock framework**: 1 reusable module (~200 lines) copied into Houdini task templates

## Key Design Decisions
1. **USD validation uses real `pxr` module** — usd-core is a pip-installable package, no Pixar build needed
2. **Houdini validation uses mock `hou`** — no Houdini license required. Mock tracks API calls structurally
3. **Solaris tasks bridge both** — mock hou entry point (`editableStage()`) returns a real USD stage for actual validation
4. **Bash tasks specify POSIX compatibility** — avoids GNU/BSD differences on macOS
5. **All templates are deterministic** — synthetic test data with known expected outputs

## Verification
After implementation:
```bash
pip install -e ".[usd]"          # Install with USD support
llm-bench info                   # Verify all tasks load
pytest tests/ -v                 # Existing tests pass
# Then run a cheap model on tier 2 tasks to smoke-test:
llm-bench run --models glm-4.7-flash --clis claude-code --tiers 2 --tasks tier2-csv-pipeline
```
