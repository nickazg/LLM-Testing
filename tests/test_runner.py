import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch
from llm_bench.runner import run_single_task, resolve_skill_path
from llm_bench.models import TaskConfig, TokenUsage
from llm_bench.adapters.base import CLIOutput


def _make_task(tmp_path, tier=1, skill=None):
    task_dir = tmp_path / f"tier{tier}" / "test-task"
    template = task_dir / "template"
    template.mkdir(parents=True)
    (template / "main.py").write_text("# placeholder")
    (task_dir / "validate.py").write_text(
        'import json, sys\nprint(json.dumps({"correctness": 1.0, "completion": 1.0}))\nsys.exit(0)'
    )
    (task_dir / "task.yaml").write_text(f"""
id: tier{tier}-test-task
name: Test Task
tier: {tier}
prompt: "Write hello world"
timeout: 60
skill: {skill if skill else 'null'}
tags: [python]
scoring:
  automated: [correctness, completion, efficiency]
  flagged: [quality]
""")
    return TaskConfig.from_dir(task_dir)


def test_run_single_task(tmp_path):
    task = _make_task(tmp_path)

    mock_output = CLIOutput(
        stdout="Done", stderr="", exit_code=0, wall_time_s=10.0,
        token_usage=TokenUsage(input=400, output=100),
        tool_calls=3, cost_usd=0.01, raw_response="raw",
    )

    with patch("llm_bench.runner.resolve_model") as mock_resolve, \
         patch("llm_bench.runner.get_adapter") as mock_get:
        mock_resolve.return_value = type("MC", (), {"env": None})()
        mock_adapter = AsyncMock()
        mock_adapter.run.return_value = mock_output
        mock_adapter.name = "claude-code"
        mock_get.return_value = mock_adapter

        result = asyncio.run(run_single_task(task, cli_name="claude-code", model="opus"))

    assert result.task_id == "tier1-test-task"
    assert result.model == "opus"
    assert result.cli == "claude-code"
    assert result.scores.correctness == 1.0
    assert result.scores.efficiency.tokens.input == 400
    assert result.prompt == "Write hello world"
    assert result.tier == 1


# --- resolve_skill_path tests ---

def _make_skill_dir(tmp_path, domain, variants_yaml=None, files=None):
    """Helper to create a skill directory with optional VARIANTS.yaml and .md files."""
    skill_dir = tmp_path / domain
    skill_dir.mkdir(parents=True)
    if variants_yaml:
        (skill_dir / "VARIANTS.yaml").write_text(variants_yaml)
    if files:
        for name, content in files.items():
            (skill_dir / name).write_text(content)
    return tmp_path


def test_resolve_skill_path_domain_with_variants_yaml(tmp_path):
    """Domain-only spec resolves via VARIANTS.yaml default."""
    skills_dir = _make_skill_dir(tmp_path, "usd-composition",
        variants_yaml="default: reference\nvariants:\n  reference:\n    description: full\n",
        files={"reference.md": "# Reference"})
    result = resolve_skill_path(skills_dir, "usd-composition")
    assert result is not None
    assert result.name == "reference.md"


def test_resolve_skill_path_explicit_variant(tmp_path):
    """domain:variant resolves to {variant}.md."""
    skills_dir = _make_skill_dir(tmp_path, "usd-composition",
        files={"task-hints.md": "# Hints", "reference.md": "# Ref"})
    result = resolve_skill_path(skills_dir, "usd-composition:task-hints")
    assert result is not None
    assert result.name == "task-hints.md"


def test_resolve_skill_path_missing_variant(tmp_path):
    """Missing variant returns None."""
    skills_dir = _make_skill_dir(tmp_path, "usd-composition",
        files={"reference.md": "# Ref"})
    result = resolve_skill_path(skills_dir, "usd-composition:nonexistent")
    assert result is None


def test_resolve_skill_path_legacy_skill_md_fallback(tmp_path):
    """Falls back to SKILL.md when no VARIANTS.yaml exists."""
    skills_dir = _make_skill_dir(tmp_path, "old-skill",
        files={"SKILL.md": "# Legacy"})
    result = resolve_skill_path(skills_dir, "old-skill")
    assert result is not None
    assert result.name == "SKILL.md"


def test_resolve_skill_path_missing_domain(tmp_path):
    """Missing domain directory returns None."""
    result = resolve_skill_path(tmp_path, "nonexistent-domain")
    assert result is None
