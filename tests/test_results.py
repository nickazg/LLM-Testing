from pathlib import Path
from llm_bench.results import save_result, load_results
from llm_bench.models import RunResult, Scores, EfficiencyMetrics


def _make_result(task_id="tier1-hello", model="opus", cli="claude-code"):
    return RunResult(
        task_id=task_id, model=model, cli=cli, skill=None,
        scores=Scores(
            correctness=1.0, completion=1.0,
            efficiency=EfficiencyMetrics(tokens=500, tool_calls=3, wall_time_s=10.0),
            quality=None, instruction_following=None,
        ),
        timestamp="2026-04-03T14:30:00Z",
    )


def test_save_and_load_result(tmp_path):
    result = _make_result()
    save_result(result, tmp_path)

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1

    loaded = load_results(tmp_path)
    assert len(loaded) == 1
    assert loaded[0]["task_id"] == "tier1-hello"
    assert loaded[0]["scores"]["correctness"] == 1.0


def test_load_multiple_results(tmp_path):
    save_result(_make_result("task-a", "opus", "claude-code"), tmp_path)
    save_result(_make_result("task-b", "qwen3", "kilo"), tmp_path)

    loaded = load_results(tmp_path)
    assert len(loaded) == 2


def test_load_results_empty_dir(tmp_path):
    loaded = load_results(tmp_path)
    assert loaded == []
