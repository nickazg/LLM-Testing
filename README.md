# LLM Bench

Automated benchmarking framework that measures LLM coding performance across CLI interfaces, with a focus on quantifying **skill uplift** — how much structured knowledge closes the gap between budget and frontier models.

## Latest Results — Phase 3 (April 2026)

**1,444 runs | 13 models | 2 CLIs | 68 tasks | 75 DSPy compilations**

[**Interactive Dashboard & Report (Live)**](https://nickazg.github.io/LLM-Testing/phase3-report.html) | [Academic Paper (Markdown)](docs/case-studies/phase3-skill-taxonomy/report.md) | [Summary Report](docs/phase3-benchmark-report.md)

### Headline Findings

| Model | Pass Rate | Notes |
|-------|-----------|-------|
| GLM-5 | **87%** | Budget champion — Z.ai coding API |
| glm-4.5-air-free | **78%** | Best free option |
| qwen3-30b | **69%** | Solid all-rounder |
| gemma-4-31b | **43%** | Capable but slow (38 timeouts excluded) |
| devstral | **24%** | 67% baseline → 0% with ANY skill injected |

- **Skills only help models above a ~65% capability threshold** — below that, skills are neutral or harmful
- **Kilo outperforms Claude Code** for most budget models (devstral: +83pp on Kilo)
- **Light workflow skills > heavy workflow skills** — concise guardrails beat prescriptive recipes
- **DSPy compilation is a precision tool**, not general uplift — helps specific weak spots, can degrade others

## The Experiment

### Skill Taxonomy

Three categories of skills, each with heavy and light intensity:

| Skill Type | What it provides | Example |
|-----------|-----------------|---------|
| **Novel Knowledge** | API info the model lacks | USD/Houdini API references |
| **Workflow/Process** | Structured guidance on known tech | LRU cache implementation approach |
| **Domain Context** | Org-specific conventions | "Our services use svc-{name} user" |

### Task Tiers

| Tier | Description | Purpose | Tasks |
|------|-------------|---------|-------|
| 1 | Single-file basics | Baseline capability | 2 |
| 2 | Multi-file patterns | Real-world complexity | 6 |
| 3 | Domain-specific, no skill | Niche knowledge baseline | 15 |
| 4 | Identical to tier 3, with skill | **Skill uplift measurement** | 45+ |

Every tier 3 task has tier 4 twins — same prompt, same validator, one variable changed: a skill is injected. The delta between tier 3 and tier 4 scores is the core measurement.

## Models

| Model | Provider | Pass Rate |
|-------|----------|-----------|
| opus4.6 | Anthropic (frontier) | 100% |
| gemini-3.1-pro | Google (frontier) | 100% |
| GLM-5 | Z.ai | 87% |
| glm-4.5-air-free | Z.ai (free) | 78% |
| qwen3-30b | Alibaba | 69% |
| gemma-4-31b | Google | 43% |
| devstral | Mistral | 24% |
| gemma-4-27b | Google (MoE) | 12% |
| glm-4.7-flash | Z.ai | 3% |

## CLI Interfaces

- [Claude Code](https://claude.ai/code) — Anthropic's CLI
- [Kilo CLI](https://kilo.ai) — Open-source coding CLI

## Scoring

| Dimension | Method |
|-----------|--------|
| Correctness | Automated — `validate.py` per task |
| Completion | Automated — expected files/state checks |
| Efficiency | Automated — tokens, tool calls, wall time |
| Quality | LLM judge (Opus, blind) |
| Instruction Following | LLM judge (Opus, blind) |

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tier 1 tasks with one model on one CLI
llm-bench run --models glm-5 --clis claude-code --tiers 1

# Filter by skill type
llm-bench run --models qwen3-30b --clis kilo --skill-types novel --tiers 4

# Run the full matrix (parallel orchestrator)
python scripts/full_benchmark.py --phase all --concurrency 4

# Launch dashboard
llm-bench dashboard --port 8080

# Run tests
pytest tests/ -v
```

## Project Structure

```
├── src/llm_bench/          # Python package
│   ├── cli.py              # CLI entry point (llm-bench command)
│   ├── runner.py           # Async orchestrator
│   ├── adapters/           # CLI-specific adapters (claude_code, kilo)
│   ├── workspace.py        # Temp dir + skill injection
│   ├── scoring.py          # Automated validation
│   ├── compiler.py         # DSPy skill compiler
│   ├── judge.py            # LLM-as-judge scorer
│   └── dashboard/          # FastAPI + Chart.js
├── tasks/tier{1-4}/        # Task definitions (68 tasks)
├── skills/                 # Skill files (26 skills + 75 compiled variants)
├── scripts/                # Benchmark orchestrator
├── results/                # JSON output (1,607 runs)
├── docs/                   # Reports and analysis
│   ├── phase3-report.html  # Interactive dashboard
│   └── case-studies/       # Academic paper + case study log
├── config/                 # Model config + API keys
└── tests/                  # 75 tests
```

## Adding Tasks

Create a directory under `tasks/tier{N}/`:

```
tasks/tier3/my-task/
├── task.yaml       # Prompt, timeout, skill metadata
├── template/       # Starting files (copied to temp dir)
└── validate.py     # Scores the result (JSON to stdout)
```

Task metadata fields:
```yaml
difficulty: 3
skill_type: novel      # novel | workflow | context
skill_intensity: heavy  # heavy | light
skill_pair: my-task     # links to baseline task
```

## Adding Skills

Place skill files in `skills/<name>/SKILL.md`. Reference them in tier 4 task.yaml:

```yaml
skill: my-skill-name
```

The harness copies the skill into `.claude/skills/` in the workspace — all CLIs discover it natively.

## Authors

Nick Grobler & Claude Code
