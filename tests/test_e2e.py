import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from llm_bench.loader import load_tasks
from llm_bench.runner import run_matrix
from llm_bench.adapters.base import CLIOutput
from llm_bench.results import load_results


def _create_task_tree(base: Path):
    task_dir = base / "tasks" / "tier1" / "hello-world"
    template = task_dir / "template"
    template.mkdir(parents=True)
    (task_dir / "task.yaml").write_text("""
id: tier1-hello-world
name: Hello World
tier: 1
prompt: "Create hello.py that prints Hello World"
timeout: 60
tags: [python]
scoring:
  automated: [correctness, completion, efficiency]
  flagged: [quality]
""")
    (task_dir / "validate.py").write_text(
        'import json, sys\nprint(json.dumps({"correctness": 1.0, "completion": 1.0}))\nsys.exit(0)'
    )
    return base / "tasks"


def test_e2e_pipeline(tmp_path):
    tasks_dir = _create_task_tree(tmp_path)
    results_dir = tmp_path / "results"

    tasks = load_tasks(tasks_dir, tiers=[1])
    assert len(tasks) == 1

    mock_output = CLIOutput(
        stdout="Created hello.py", stderr="", exit_code=0,
        wall_time_s=8.0, tokens=400, tool_calls=2, cost_usd=0.005,
    )

    with patch("llm_bench.runner.get_adapter") as mock_get:
        mock_adapter = AsyncMock()
        mock_adapter.run.return_value = mock_output
        mock_adapter.name = "claude-code"
        mock_get.return_value = mock_adapter

        results = asyncio.run(run_matrix(
            tasks=tasks,
            cli_names=["claude-code"],
            models=["opus"],
            results_dir=results_dir,
        ))

    assert len(results) == 1
    r = results[0]
    assert r.task_id == "tier1-hello-world"
    assert r.scores.correctness == 1.0
    assert r.scores.efficiency.tokens == 400

    saved = load_results(results_dir)
    assert len(saved) == 1
    assert saved[0]["task_id"] == "tier1-hello-world"


def test_e2e_multi_model_multi_cli(tmp_path):
    tasks_dir = _create_task_tree(tmp_path)
    results_dir = tmp_path / "results"

    tasks = load_tasks(tasks_dir, tiers=[1])

    mock_output = CLIOutput(
        stdout="Done", stderr="", exit_code=0,
        wall_time_s=10.0, tokens=600, tool_calls=4, cost_usd=0.01,
    )

    with patch("llm_bench.runner.get_adapter") as mock_get:
        mock_adapter = AsyncMock()
        mock_adapter.run.return_value = mock_output
        mock_adapter.name = "test"
        mock_get.return_value = mock_adapter

        results = asyncio.run(run_matrix(
            tasks=tasks,
            cli_names=["claude-code", "kilo"],
            models=["opus", "qwen3-30b"],
            results_dir=results_dir,
        ))

    assert len(results) == 4
    saved = load_results(results_dir)
    assert len(saved) == 4
