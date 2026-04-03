from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from llm_bench.adapters.base import CLIOutput
from llm_bench.models import EfficiencyMetrics


async def run_validator(workspace: Path, timeout: int = 30) -> dict:
    validate_py = workspace / "validate.py"
    if not validate_py.exists():
        return {"correctness": 0.0, "completion": 0.0, "error": "No validate.py found"}

    try:
        result = subprocess.run(
            [sys.executable, str(validate_py)],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"correctness": 0.0, "completion": 0.0, "error": "Validator timed out"}
    except Exception as e:
        return {"correctness": 0.0, "completion": 0.0, "error": str(e)}

    scores = {}
    if result.stdout.strip():
        try:
            scores = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            pass

    if not scores:
        scores = {
            "correctness": 1.0 if result.returncode == 0 else 0.0,
            "completion": 1.0 if result.returncode == 0 else 0.0,
        }

    return scores


def score_efficiency(output: CLIOutput) -> EfficiencyMetrics:
    return EfficiencyMetrics(
        tokens=output.token_usage,
        tool_calls=output.tool_calls,
        wall_time_s=output.wall_time_s,
        cost_usd=output.cost_usd,
    )
