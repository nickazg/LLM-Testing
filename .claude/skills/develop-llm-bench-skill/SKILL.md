---
name: develop-llm-bench-skill
description: Use when creating benchmark skills that get injected into CLI workspaces for tier 4 tasks. These are the skills tested for uplift measurement, not Claude Code project skills.
---

# Creating LLM Bench Skills

## What These Skills Are

These are **benchmark skills** — domain knowledge files injected into CLI workspaces during tier 4 task runs. They test whether providing structured knowledge to a model improves its performance on niche tasks.

They live in `skills/` (project root), NOT in `.claude/skills/` (those are Claude Code project skills for developing this repo).

## Skill Structure

```
skills/{skill-name}/
└── SKILL.md
```

That's it. One directory, one SKILL.md file. The harness copies this into `.claude/skills/{skill-name}/SKILL.md` in the temp workspace before the CLI runs.

## SKILL.md Format

```yaml
---
name: {skill-name}
description: {When to use this skill — matched against task context by the CLI}
---

{Markdown content — the domain knowledge}
```

## What Goes in a Skill

A skill provides the knowledge an expert would have that isn't in the model's training data (or is poorly represented). Think of it as a concise briefing document.

**Include:**
- API reference for the specific domain (function signatures, parameters, return types)
- Common patterns and idioms ("always do X before Y")
- Gotchas and pitfalls ("Z silently fails if you don't set W first")
- Minimal working examples for key operations
- Constraints the model wouldn't know (version-specific behavior, undocumented quirks)

**Do NOT include:**
- The solution to any specific task
- Generic programming advice
- Information easily found in mainstream docs (Python stdlib, etc.)
- Excessive detail — keep it under 2000 words. Models have context limits.

## Writing Effective Skills

**The skill should make a bad attempt good, not make a good attempt trivial.**

1. **Identify the knowledge gap:** What would a model get wrong without domain expertise? That's what the skill should cover.
2. **Be reference-style, not tutorial-style:** Quick-lookup format, not a learning guide. The model is a skilled programmer — it just doesn't know this specific domain.
3. **Include the non-obvious:** Focus on what's surprising or counterintuitive. Skip what's obvious from function names.
4. **Test by imagining the task:** Would this skill prevent the common mistakes on the tier 3 task? If not, add what's missing.

## Example Skill

```markdown
---
name: usd-basics
description: Pixar USD (Universal Scene Description) stage composition, layer management, and prim operations
---

# USD Quick Reference

## Stage Creation
- Always create a stage with `Usd.Stage.CreateNew("file.usda")` or `CreateInMemory()`
- Call `stage.GetRootLayer().Save()` to persist — stages don't auto-save
- Default up-axis is Y. Set with `UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)`

## Prim Operations
- Define prims: `stage.DefinePrim("/World/Mesh", "Mesh")`
- The path MUST start with `/` — relative paths silently fail
- Check prim validity: `prim.IsValid()` before operating

## Layer Composition
- Sublayers: `stage.GetRootLayer().subLayerPaths.append("other.usda")`
- References: `prim.GetReferences().AddReference("asset.usda")`
- Sublayers are strongest-first (index 0 wins). This is counterintuitive.

## Common Gotchas
- `GetAttribute().Get()` returns `None` if attribute doesn't exist — no error raised
- Xform ops accumulate. Use `UsdGeom.Xformable(prim).ClearXformOpOrder()` to reset
- Time-sampled values need `Usd.TimeCode.Default()` or a frame number, not bare `.Get()`
```

## Connecting a Skill to a Task

1. Create the skill in `skills/{skill-name}/SKILL.md`
2. Create or identify the tier 3 task it supports
3. Clone the tier 3 task to `tasks/tier4/{same-name}/`
4. In the tier 4 `task.yaml`, set `skill: {skill-name}`
5. Run `llm-bench info` to verify both show up

## Skill Quality Checklist

Before finalizing a skill, verify:

- [ ] Would a domain expert nod at every statement? No hallucinated APIs.
- [ ] Does it cover the specific gotchas relevant to the paired tier 3 task?
- [ ] Is it under 2000 words? Trim ruthlessly.
- [ ] Is it reference-style, not tutorial-style?
- [ ] Does it avoid giving away the solution to any task?
- [ ] Is the `name` field kebab-case and matches the directory name?
- [ ] Is the `description` field specific enough for CLI skill matching?

## Existing Skills

Check `skills/` for examples. Run `llm-bench info` to see all registered skills and which tasks reference them.
