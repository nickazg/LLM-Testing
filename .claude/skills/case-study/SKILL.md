---
name: case-study
description: Track experimental findings and generate formal case study reports. Use when running experiments, analyzing results, or when asked to log/report findings. Supports ongoing tracking across sessions and formal paper generation.
---

# Case Study Tracker

Track experimental findings in a structured log and generate formal reports. Designed for ongoing research across multiple sessions — captures what would otherwise be lost between context windows.

## Commands

### `log <entry>` — Manual Capture
User explicitly asks to log something. Create a structured entry in the log file.

**Process:**
1. Parse the user's statement into category, title, body, and tags
2. Find evidence links (result files, commits, file paths) that support the claim
3. Append the entry to the active case study's `log.yaml`
4. Confirm what was logged with a one-line summary

### `checkpoint` — Prompted Review
Review recent work and propose log entries for approval.

**Process:**
1. Review what has happened since the last checkpoint (benchmark runs, analysis, code changes)
2. Propose 2-5 structured entries with categories and titles
3. Present them to the user for approval/edit/rejection
4. Append approved entries to `log.yaml`

### `report [format]` — Generate Report
Compile the log into a formal document.

**Formats:**
- `report paper` — academic-style paper (default)
- `report brief` — technical case study for practitioners
- `report raw` — chronological narrative of all entries (session handoff)

**Process:**
1. Read the full `log.yaml`
2. Where entries link to result files in `evidence`, load actual scores to build tables
3. Generate the report in the requested format (see Report Templates below)
4. Write to `report.md`, `report-brief.md`, or `report-raw.md` in the case study directory
5. Show the user a summary of what was generated

### `status` — Current State
Show log stats: total entries, entries by category, latest 5 entries, active session name.

## Auto-Capture Triggers

When this skill is active, AUTOMATICALLY log the following without asking:

| Trigger | Category | What to Capture |
|---------|----------|-----------------|
| Benchmark run completes | `result` | Model, CLI, tasks, scores, duration, pass/fail counts |
| DSPy compilation finishes | `result` | Config (teacher, target, metric mode), output score, variant name |
| New result files appear | `result` | Summary of scores from the new files |

These are factual records — no interpretation needed, so auto-capture is safe.

## Prompted Checkpoint Triggers

At these moments, PROPOSE entries for the user to approve:

| Trigger | Likely Categories |
|---------|-------------------|
| After analyzing benchmark results | `finding`, `surprise` |
| When a hypothesis is stated or updated | `hypothesis` |
| When something contradicts expectations | `surprise` |
| When methodology changes | `method` |
| After completing a plan or major task | `finding`, `method` |

**Format the proposal as:**
```
Checkpoint — I'd log these findings:
1. [finding] "Title here" — one-line summary
2. [surprise] "Title here" — one-line summary
Approve all / edit / skip?
```

## Log Location & Format

**Directory structure:**
```
docs/case-studies/{study-name}/
├── log.yaml           # Structured entry log
├── report.md          # Academic paper (generated)
├── report-brief.md    # Technical brief (generated)
└── report-raw.md      # Chronological narrative (generated)
```

**Entry schema:**
```yaml
- id: "001"
  date: "YYYY-MM-DD"
  category: result|finding|hypothesis|surprise|method|context
  title: "Short descriptive title"
  body: "Detailed explanation. Include numbers, scores, and specifics."
  evidence:
    - "path/to/result/file.json"
    - "path/to/source/file.py:42"
    - "git:abc1234"
  tags: [tag1, tag2]
  session: "YYYY-MM-DD-session-name"
  retrospective: false  # true if reconstructed from history
```

**Category definitions:**
- `result` — raw experimental output (benchmark scores, compilation metrics). Factual, no interpretation.
- `finding` — analytical conclusion drawn from one or more results. Interpretation with evidence.
- `hypothesis` — proposed explanation for observed behavior. Testable, may be validated or refuted later.
- `surprise` — something that contradicts prior assumptions or expectations. Highlight in reports.
- `method` — methodology decision, tool choice, or experimental design change. Captures the "why" of how we work.
- `context` — setup, configuration, environment info. Background needed to reproduce.

## Report Templates

### Academic Paper (`report paper`)

Write to `report.md`. Structure:

```markdown
# {Study Title}

## Abstract
150-word summary. State the research question, method, key finding, and implication.

## 1. Introduction
- Motivation: why this matters
- Research questions (derive from hypothesis entries)
- Scope and limitations

## 2. Methodology
- Framework architecture (from method + context entries)
- Task design and tier system
- Scoring approach
- Skill injection mechanism
- Models and CLIs tested

## 3. Experimental Setup
- Hardware/environment context
- Model configurations (from context entries)
- Skill variants tested
- DSPy compilation configuration

## 4. Results
Organized by experiment/session. For each:
- What was tested
- Data tables (compute from evidence-linked result files where possible)
- Key numbers

## 5. Discussion
- Synthesize findings into themes (from finding + hypothesis entries)
- Highlight surprises (from surprise entries) as callout blocks
- Address each research question
- Threats to validity (single-run variance, CLI confound, proxy metric limitations)

## 6. Conclusion
- Summary of contributions
- Implications for practitioners
- Future work

## Appendix
- Full result tables
- Skill content samples
- Tool versions and configuration
```

### Technical Brief (`report brief`)

Write to `report-brief.md`. Structure:

```markdown
# {Study Title} — Technical Brief

## Executive Summary
3-5 bullet points of headline findings.

## Setup
What we built, what we tested, how scoring works. Keep to ~300 words.

## Experiments & Findings
Chronological sections per session/experiment. Each has:
- **What we tested** — one sentence
- **Results** — table or bullet scores
- **What we learned** — 2-3 sentences

## Key Insights
Numbered list of the most important takeaways, derived from finding + surprise entries.

## Implications
What this means for skill design, model selection, and benchmarking in practice.

## Next Steps
Open questions and planned work.
```

### Raw Narrative (`report raw`)

Write to `report-raw.md`. Chronological dump of all entries grouped by session, minimal formatting. Useful as a handoff document between sessions or context windows.

## Starting a New Case Study

When starting fresh, create the directory and an empty `log.yaml`:
```yaml
# Case Study: {title}
# Started: {date}
# Description: {one-line description}
entries: []
```

## Seeding from History

When reconstructing past work, set `retrospective: true` on all entries. Use these sources:
- `.claude/HISTORY.md` — session dates, summaries, key findings
- `.claude/CURRENT-STATE.md` — accumulated theory
- `results/` directory — actual scores (load JSON, extract scores)
- `skills/*/VARIANTS.yaml` — compilation metadata
- Git log — timeline and commit messages

## Session Management

Each session gets a name like `YYYY-MM-DD-short-description`. All entries logged during that session share the session field. At the start of a new session, announce:

```
Case study active: {study-name}
Session: {session-name}
Log has {N} entries across {M} sessions.
```

## Important Rules

1. **Evidence over assertion** — every finding and surprise MUST link to at least one evidence path
2. **Hypotheses are provisional** — mark them clearly, track whether they're later validated or refuted
3. **Auto-capture is facts only** — never auto-log interpretations, only raw results
4. **Checkpoints need approval** — always present proposed analytical entries before logging
5. **Reports pull real data** — when evidence links to result JSON files, load the actual scores for tables rather than relying on log body text alone
6. **Retrospective honesty** — reconstructed entries are clearly marked, don't pretend they were live-captured
