---
name: develop-llm-bench-task
description: Use when creating new benchmark tasks for llm-bench. Guides creation of task.yaml, template/, and validate.py with correct structure and scoring.
---

# Creating LLM Bench Tasks

## Task Structure

Every task is a self-contained directory under `tasks/tier{N}/`:

```
tasks/tier{N}/{task-name}/
├── task.yaml       # Task definition
├── template/       # Starting files (copied to temp workspace before run)
│   └── .gitkeep    # Can be empty for "from scratch" tasks
└── validate.py     # Scores the result (MUST output JSON to stdout)
```

## Tier System

| Tier | Purpose | Skill field |
|------|---------|-------------|
| 1 | Single-file, well-known domain (basics) | `null` |
| 2 | Multi-file, common patterns (real-world) | `null` |
| 3 | Domain-specific, niche knowledge needed | `null` |
| 4 | **Identical to a tier 3 task, with a skill** | Set to skill name |

**Critical rule:** Every tier 4 task MUST be a clone of an existing tier 3 task. Same prompt, same template, same validate.py. The ONLY difference is the `skill` field points to a skill in `skills/`. This is what makes the skill uplift measurement valid.

## task.yaml Format

```yaml
id: tier{N}-{kebab-case-name}       # Unique ID, must match: tier{N}-{name}
name: "Human Readable Name"          # Short display name
tier: {1|2|3|4}
prompt: "Exact prompt sent to the model. Be specific about expected filenames and behavior."
timeout: 120                          # Seconds before the CLI is killed
skill: null                           # Or skill directory name for tier 4 (e.g. "usd-basics")
tags: [python, domain, ...]           # For filtering
scoring:
  automated:                          # Scored by validate.py
    - correctness
    - completion
    - efficiency
  flagged:                            # Scored by LLM judge (optional)
    - quality
    - instruction_following
```

## Writing Prompts

- **Be explicit about filenames:** "Create a file called `fizzbuzz.py`" not "Create a fizzbuzz program"
- **Be explicit about behavior:** "prints to stdout" not "outputs"
- **Don't leak the solution:** The prompt should describe WHAT, not HOW
- **Keep it self-contained:** The model should not need external resources
- **Match the tier:** Tier 1 = one file, obvious approach. Tier 3 = domain expertise needed.

## validate.py Requirements

The validator MUST:
1. Run from the workspace root directory (`Path(".")`)
2. Print a JSON object to stdout: `{"correctness": 0.0-1.0, "completion": 0.0-1.0}`
3. Exit with code 0 on pass, 1 on fail (but JSON scores take precedence)

**Pattern:**

```python
"""Validator for {task-id}."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}

# 1. Check expected files exist
target = Path(".") / "expected_file.py"
if not target.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

# 2. Run the code and check output
try:
    result = subprocess.run(
        [sys.executable, str(target)],
        capture_output=True, text=True, timeout=10,
    )
    # Check output matches expected
    if "expected output" in result.stdout:
        scores["correctness"] = 1.0
except Exception:
    pass

print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.5 else 1)
```

**Scoring guidelines:**
- `completion`: Did the model create the expected files? Binary or fractional.
- `correctness`: Does the code produce correct output? Can be fractional (e.g. 95/100 lines correct = 0.95).
- Use `subprocess.run` with `timeout=10` to execute created code safely.
- Use `sys.executable` to ensure the same Python interpreter is used.

## template/ Directory

- For "from scratch" tasks: leave empty (just `.gitkeep`)
- For "modify existing code" tasks: include the starting files
- For "fix a bug" tasks: include the broken code
- Never include the solution or hints

## Creating a Tier 3/4 Pair

1. Create the tier 3 task first (no skill)
2. Copy the entire directory to `tasks/tier4/{same-name}/`
3. In the tier 4 copy, change ONLY `task.yaml`:
   - `id:` → change prefix to `tier4-`
   - `tier:` → change to `4`
   - `skill:` → set to the skill directory name from `skills/`
4. **Do NOT change the prompt, template, or validate.py**

## Process

1. Decide the tier based on domain specificity
2. Create the directory: `tasks/tier{N}/{task-name}/`
3. Write `task.yaml` with a clear, specific prompt
4. Create `template/` with starting files (or empty)
5. Write `validate.py` that objectively scores the output
6. Test the validator works: `cd tasks/tier{N}/{task-name}/template && python ../validate.py`
7. Verify the task loads: `llm-bench info`
8. If tier 3, consider creating the tier 4 twin with a matching skill

## Existing Tasks for Reference

Check `tasks/` for examples. Run `llm-bench info` to see all registered tasks.
