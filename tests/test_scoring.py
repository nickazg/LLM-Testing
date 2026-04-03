import asyncio
from llm_bench.scoring import run_validator, score_efficiency
from llm_bench.adapters.base import CLIOutput
from llm_bench.models import TokenUsage


def test_run_validator_pass(tmp_path):
    (tmp_path / "validate.py").write_text(
        'import json, sys\nprint(json.dumps({"correctness": 1.0, "completion": 1.0}))\nsys.exit(0)'
    )
    result = asyncio.run(run_validator(tmp_path))
    assert result["correctness"] == 1.0
    assert result["completion"] == 1.0


def test_run_validator_fail(tmp_path):
    (tmp_path / "validate.py").write_text(
        'import json, sys\nprint(json.dumps({"correctness": 0.0, "completion": 0.5}))\nsys.exit(1)'
    )
    result = asyncio.run(run_validator(tmp_path))
    assert result["correctness"] == 0.0


def test_run_validator_no_json_output(tmp_path):
    (tmp_path / "validate.py").write_text("import sys; sys.exit(0)")
    result = asyncio.run(run_validator(tmp_path))
    assert result["correctness"] == 1.0


def test_run_validator_crash(tmp_path):
    (tmp_path / "validate.py").write_text("raise Exception('boom')")
    result = asyncio.run(run_validator(tmp_path))
    assert result["correctness"] == 0.0


def test_score_efficiency():
    output = CLIOutput(
        stdout="done", stderr="", exit_code=0,
        wall_time_s=30.0,
        token_usage=TokenUsage(input=1500, output=500, thinking=100),
        tool_calls=5, cost_usd=0.03,
    )
    eff = score_efficiency(output)
    assert eff.tokens.input == 1500
    assert eff.tokens.output == 500
    assert eff.tokens.thinking == 100
    assert eff.tool_calls == 5
    assert eff.wall_time_s == 30.0
    assert eff.cost_usd == 0.03
