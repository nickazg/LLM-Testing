from __future__ import annotations

import json
from pathlib import Path
from llm_bench.models import RunResult


def save_result(result: RunResult, results_dir: Path) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{result.task_id}_{result.cli}_{result.model}_{result.timestamp}.json"
    filename = filename.replace(":", "-").replace("/", "-")
    path = results_dir / filename
    path.write_text(result.to_json())
    return path


def load_results(results_dir: Path) -> list[dict]:
    if not results_dir.exists():
        return []
    results = []
    for f in sorted(results_dir.glob("*.json")):
        try:
            results.append(json.loads(f.read_text()))
        except json.JSONDecodeError:
            continue
    return results
