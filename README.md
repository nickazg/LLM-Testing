# LLM Bench

Automated benchmarking framework that measures LLM coding performance across CLI interfaces, with a focus on quantifying **skill uplift** — how much structured knowledge closes the gap between budget and frontier models.

## The Experiment

Models are tested across a 4-tier task system:

| Tier | Description | Purpose |
|------|-------------|---------|
| 1 | Single-file, well-known domain | Baseline capability |
| 2 | Multi-file, common patterns | Real-world complexity |
| 3 | Domain-specific, no skill | Niche knowledge baseline |
| 4 | Identical to tier 3, with skill | **Skill uplift measurement** |

Every tier 3 task has a tier 4 twin — same prompt, same validator, one variable changed: a skill is injected. The delta between tier 3 and tier 4 scores per model is the core insight.

## Models

- Qwen3 Coder 30B
- MinimaxM2.7
- GLM-5
- Gemma 4 31B
- Opus 4.6

## CLI Interfaces

- [Claude Code](https://claude.ai/code)
- [Open Code](https://opencode.ai)
- [Kilo CLI](https://kilo.ai)

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
llm-bench run --models opus --clis claude-code --tiers 1

# Run the full matrix
llm-bench run --models opus,qwen3-30b --clis claude-code,open-code,kilo --tiers 1,2,3,4

# Launch dashboard
llm-bench dashboard --port 8080

# Run tests
pytest tests/ -v
```

## Project Structure

```
├── src/llm_bench/        # Python package
│   ├── cli.py            # CLI entry point (llm-bench command)
│   ├── runner.py          # Async orchestrator
│   ├── adapters/          # CLI-specific adapters
│   ├── workspace.py       # Temp dir + skill injection
│   ├── scoring.py         # Automated validation
│   ├── judge.py           # LLM-as-judge scorer
│   └── dashboard/         # FastAPI + Chart.js
├── tasks/tier{1-4}/       # Task definitions
├── skills/                # Skill files for tier 4
├── results/               # JSON output (gitignored)
└── tests/                 # 44 tests
```

## Adding Tasks

Create a directory under `tasks/tier{N}/`:

```
tasks/tier1/my-task/
├── task.yaml       # Prompt, timeout, scoring config
├── template/       # Starting files (copied to temp dir)
└── validate.py     # Scores the result (JSON to stdout)
```

## Adding Skills

Place skill files in `skills/<name>/SKILL.md`. Reference them in tier 4 task.yaml:

```yaml
skill: my-skill-name
```

The harness copies the skill into `.claude/skills/` in the workspace — all three CLIs discover it natively.
