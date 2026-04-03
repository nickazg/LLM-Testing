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
