from pathlib import Path
from llm_bench.models import TaskConfig


def load_tasks(
    tasks_dir: Path,
    tiers: list[int] | None = None,
    task_ids: list[str] | None = None,
) -> list[TaskConfig]:
    tasks = []
    for tier_dir in sorted(tasks_dir.iterdir()):
        if not tier_dir.is_dir() or not tier_dir.name.startswith("tier"):
            continue
        tier_num = int(tier_dir.name.replace("tier", ""))
        if tiers and tier_num not in tiers:
            continue
        for task_dir in sorted(tier_dir.iterdir()):
            yaml_path = task_dir / "task.yaml"
            if not yaml_path.exists():
                continue
            config = TaskConfig.from_dir(task_dir)
            if task_ids and config.id not in task_ids:
                continue
            tasks.append(config)
    return tasks
