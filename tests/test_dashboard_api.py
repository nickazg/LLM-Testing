import json
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient


def _seed_results(results_dir: Path):
    for i, (model, cli) in enumerate([("opus", "claude-code"), ("qwen3", "kilo")]):
        data = {
            "task_id": "tier1-hello",
            "model": model,
            "cli": cli,
            "skill": None,
            "scores": {
                "correctness": 1.0 if model == "opus" else 0.8,
                "completion": 1.0,
                "efficiency": {"tokens": 500 + i * 200, "tool_calls": 3, "wall_time_s": 10.0},
                "quality": None,
                "instruction_following": None,
            },
            "timestamp": f"2026-04-03T14:3{i}:00Z",
        }
        (results_dir / f"result_{i}.json").write_text(json.dumps(data))


def test_api_results(tmp_path):
    _seed_results(tmp_path)
    with patch("llm_bench.dashboard.app.RESULTS_DIR", tmp_path):
        from llm_bench.dashboard.app import app
        client = TestClient(app)
        response = client.get("/api/results")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_api_index(tmp_path):
    with patch("llm_bench.dashboard.app.RESULTS_DIR", tmp_path):
        from llm_bench.dashboard.app import app
        client = TestClient(app)
        response = client.get("/")
    assert response.status_code == 200
    assert "LLM Bench Dashboard" in response.text
