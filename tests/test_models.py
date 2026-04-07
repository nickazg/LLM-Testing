from llm_bench.models import TaskConfig, RunResult, Scores, EfficiencyMetrics, TokenUsage


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


def test_task_config_with_taxonomy_fields(tmp_path):
    task_dir = tmp_path / "tier4" / "lru-cache-light"
    task_dir.mkdir(parents=True)
    (task_dir / "task.yaml").write_text(
        """
id: tier4-lru-cache-workflow-light
name: "LRU Cache — Workflow Light"
tier: 4
prompt: "Implement an LRU cache."
timeout: 300
skill: lru-cache-workflow-light
difficulty: 3
skill_type: workflow
skill_intensity: light
skill_pair: lru-cache
tags: [python, algorithms]
scoring:
  automated: [correctness]
  flagged: []
"""
    )
    config = TaskConfig.from_dir(task_dir)
    assert config.difficulty == 3
    assert config.skill_type == "workflow"
    assert config.skill_intensity == "light"
    assert config.skill_pair == "lru-cache"


def test_task_config_taxonomy_fields_default_none(tmp_path):
    """Old task.yamls without new fields should still load with None defaults."""
    task_dir = tmp_path / "tier1" / "basic"
    task_dir.mkdir(parents=True)
    (task_dir / "task.yaml").write_text(
        """
id: tier1-basic
name: Basic
tier: 1
prompt: Do something
timeout: 60
tags: []
scoring:
  automated: [correctness]
  flagged: []
"""
    )
    config = TaskConfig.from_dir(task_dir)
    assert config.difficulty is None
    assert config.skill_type is None
    assert config.skill_intensity is None
    assert config.skill_pair is None


def test_run_result_to_json():
    result = RunResult(
        task_id="tier1-hello",
        model="qwen3-30b",
        cli="claude-code",
        skill=None,
        scores=Scores(
            correctness=1.0,
            completion=1.0,
            efficiency=EfficiencyMetrics(
                tokens=TokenUsage(input=1000, output=500, thinking=200),
                tool_calls=3,
                wall_time_s=22.5,
            ),
            quality=None,
            instruction_following=None,
        ),
        timestamp="2026-04-03T14:30:00Z",
        prompt="Write hello world",
        raw_output="Done.",
        tier=1,
    )
    data = result.to_dict()
    assert data["task_id"] == "tier1-hello"
    assert data["scores"]["correctness"] == 1.0
    assert data["scores"]["efficiency"]["tokens"]["input"] == 1000
    assert data["scores"]["efficiency"]["tokens"]["output"] == 500
    assert data["scores"]["efficiency"]["tokens"]["thinking"] == 200
    assert data["scores"]["quality"] is None
    assert data["prompt"] == "Write hello world"
    assert data["tier"] == 1


def test_run_result_taxonomy_fields_in_json():
    result = RunResult(
        task_id="tier4-lru-cache-workflow-light",
        model="qwen3-30b",
        cli="kilo",
        skill="lru-cache-workflow-light",
        scores=Scores(correctness=0.8),
        timestamp="2026-04-07T10:00:00Z",
        tier=4,
        difficulty=3,
        skill_type="workflow",
        skill_intensity="light",
        skill_pair="lru-cache",
    )
    data = result.to_dict()
    assert data["difficulty"] == 3
    assert data["skill_type"] == "workflow"
    assert data["skill_intensity"] == "light"
    assert data["skill_pair"] == "lru-cache"


def test_token_usage_total():
    t = TokenUsage(input=100, output=50, thinking=25)
    assert t.total == 175
