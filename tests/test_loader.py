from pathlib import Path
from llm_bench.loader import load_tasks


def test_load_tasks_filters_by_tier(tmp_path):
    t1 = tmp_path / "tasks" / "tier1" / "hello"
    t1.mkdir(parents=True)
    (t1 / "task.yaml").write_text(
        """
id: tier1-hello
name: Hello
tier: 1
prompt: Write hello world
timeout: 60
tags: [python]
scoring:
  automated: [correctness]
  flagged: []
"""
    )

    t2 = tmp_path / "tasks" / "tier2" / "api"
    t2.mkdir(parents=True)
    (t2 / "task.yaml").write_text(
        """
id: tier2-api
name: API
tier: 2
prompt: Build an API
timeout: 120
tags: [python]
scoring:
  automated: [correctness]
  flagged: []
"""
    )

    tasks = load_tasks(tmp_path / "tasks", tiers=[1])
    assert len(tasks) == 1
    assert tasks[0].id == "tier1-hello"


def test_load_tasks_all_tiers(tmp_path):
    for tier, tid in [(1, "hello"), (2, "api")]:
        d = tmp_path / "tasks" / f"tier{tier}" / tid
        d.mkdir(parents=True)
        (d / "task.yaml").write_text(
            f"""
id: tier{tier}-{tid}
name: {tid}
tier: {tier}
prompt: Do something
timeout: 60
tags: []
scoring:
  automated: [correctness]
  flagged: []
"""
        )

    tasks = load_tasks(tmp_path / "tasks", tiers=[1, 2])
    assert len(tasks) == 2


def test_load_tasks_by_id(tmp_path):
    for tid in ["hello", "goodbye"]:
        d = tmp_path / "tasks" / "tier1" / tid
        d.mkdir(parents=True)
        (d / "task.yaml").write_text(
            f"""
id: tier1-{tid}
name: {tid}
tier: 1
prompt: Do {tid}
timeout: 60
tags: []
scoring:
  automated: [correctness]
  flagged: []
"""
        )

    tasks = load_tasks(tmp_path / "tasks", tiers=[1], task_ids=["tier1-hello"])
    assert len(tasks) == 1
    assert tasks[0].id == "tier1-hello"


def _create_taxonomy_tasks(tmp_path):
    """Helper to create tasks with taxonomy fields for filter tests."""
    tasks_dir = tmp_path / "tasks"
    configs = [
        ("tier3", "lru-cache", 3, None, None, None),
        ("tier4", "lru-cache-heavy", 3, "workflow", "heavy", "lru-cache"),
        ("tier4", "lru-cache-light", 3, "workflow", "light", "lru-cache"),
        ("tier4", "usd-solaris", 3, "novel", "heavy", "houdini-solaris"),
        ("tier4", "git-hook-ctx", 3, "context", "heavy", "git-hook"),
    ]
    for tier, name, diff, stype, sintensity, spair in configs:
        d = tasks_dir / tier / name
        d.mkdir(parents=True)
        yaml = f"""
id: {tier}-{name}
name: {name}
tier: {int(tier[-1])}
prompt: Do {name}
timeout: 60
difficulty: {diff}
"""
        if stype:
            yaml += f"skill: {name}-skill\nskill_type: {stype}\nskill_intensity: {sintensity}\nskill_pair: {spair}\n"
        else:
            yaml += "skill: null\n"
        yaml += "tags: []\nscoring:\n  automated: [correctness]\n  flagged: []\n"
        (d / "task.yaml").write_text(yaml)
    return tasks_dir


def test_load_tasks_filter_by_skill_type(tmp_path):
    tasks_dir = _create_taxonomy_tasks(tmp_path)
    tasks = load_tasks(tasks_dir, skill_types=["workflow"])
    assert len(tasks) == 2
    assert all(t.skill_type == "workflow" for t in tasks)


def test_load_tasks_filter_by_difficulty(tmp_path):
    tasks_dir = _create_taxonomy_tasks(tmp_path)
    tasks = load_tasks(tasks_dir, difficulties=[3])
    assert len(tasks) == 5  # all have difficulty 3


def test_load_tasks_filter_by_skill_type_and_tier(tmp_path):
    tasks_dir = _create_taxonomy_tasks(tmp_path)
    tasks = load_tasks(tasks_dir, tiers=[4], skill_types=["novel"])
    assert len(tasks) == 1
    assert tasks[0].skill_type == "novel"
