from llm_bench.models import TaskConfig, RunResult, Scores, EfficiencyMetrics


def test_task_config_from_yaml(tmp_path):
    task_dir = tmp_path / "tier1" / "hello-world"
    task_dir.mkdir(parents=True)
    (task_dir / "task.yaml").write_text(
        """
id: tier1-hello-world
name: "Hello World"
tier: 1
prompt: "Write a hello world program in Python."
timeout: 120
skill: null
tags: [python, basics]
scoring:
  automated:
    - correctness
    - completion
    - efficiency
  flagged:
    - quality
    - instruction_following
"""
    )
    config = TaskConfig.from_dir(task_dir)
    assert config.id == "tier1-hello-world"
    assert config.tier == 1
    assert config.timeout == 120
    assert config.skill is None
    assert "correctness" in config.scoring_automated
    assert "quality" in config.scoring_flagged


def test_task_config_with_skill(tmp_path):
    task_dir = tmp_path / "tier4" / "usd-stage"
    task_dir.mkdir(parents=True)
    (task_dir / "task.yaml").write_text(
        """
id: tier4-usd-stage
name: "USD Stage Composition"
tier: 4
prompt: "Create a USD stage with two referenced layers."
timeout: 300
skill: usd-basics
tags: [python, usd, vfx]
scoring:
  automated:
    - correctness
    - completion
    - efficiency
  flagged:
    - quality
    - instruction_following
"""
    )
    config = TaskConfig.from_dir(task_dir)
    assert config.skill == "usd-basics"
    assert config.tier == 4


def test_run_result_to_json():
    result = RunResult(
        task_id="tier1-hello",
        model="qwen3-30b",
        cli="claude-code",
        skill=None,
        scores=Scores(
            correctness=1.0,
            completion=1.0,
            efficiency=EfficiencyMetrics(tokens=1500, tool_calls=3, wall_time_s=22.5),
            quality=None,
            instruction_following=None,
        ),
        timestamp="2026-04-03T14:30:00Z",
    )
    data = result.to_dict()
    assert data["task_id"] == "tier1-hello"
    assert data["scores"]["correctness"] == 1.0
    assert data["scores"]["efficiency"]["tokens"] == 1500
    assert data["scores"]["quality"] is None
