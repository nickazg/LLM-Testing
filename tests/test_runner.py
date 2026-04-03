import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch
from llm_bench.runner import run_single_task
from llm_bench.models import TaskConfig
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
        stdout="Done", stderr="", exit_code=0,
        wall_time_s=10.0, tokens=500, tool_calls=3, cost_usd=0.01,
    )

    with patch("llm_bench.runner.get_adapter") as mock_get:
        mock_adapter = AsyncMock()
        mock_adapter.run.return_value = mock_output
        mock_adapter.name = "claude-code"
        mock_get.return_value = mock_adapter

        result = asyncio.run(run_single_task(task, cli_name="claude-code", model="opus"))

    assert result.task_id == "tier1-test-task"
    assert result.model == "opus"
    assert result.cli == "claude-code"
    assert result.scores.correctness == 1.0
    assert result.scores.efficiency.tokens == 500
