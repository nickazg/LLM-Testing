from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from llm_bench.adapters import get_adapter
from llm_bench.models import TaskConfig, RunResult, Scores
from llm_bench.scoring import run_validator, score_efficiency
from llm_bench.workspace import prepare_workspace


def _find_env_file(config_dir: Path, cli_name: str, model: str) -> str | None:
    """Auto-discover env file at config/{cli}.{model}.env"""
    env_path = config_dir / f"{cli_name}.{model}.env"
    if env_path.exists():
        return str(env_path)
    return None


def _default_log(msg: str):
    print(msg, flush=True)


async def run_single_task(
    task: TaskConfig,
    cli_name: str,
    model: str,
    skills_dir: Path | None = None,
    config_dir: Path | None = None,
    log: Callable[[str], None] = _default_log,
    **adapter_kwargs,
) -> RunResult:
    skill_path = None
    if task.skill and skills_dir:
        skill_path = skills_dir / task.skill / "SKILL.md"
        if not skill_path.exists():
            skill_path = None

    workspace = prepare_workspace(
        task_dir=task.task_dir,
        cli_name=cli_name,
        skill_path=skill_path,
    )
    workspace_path = Path(workspace.name)

    try:
        # Auto-discover env file if not explicitly provided
        if "env_file" not in adapter_kwargs and config_dir:
            env_file = _find_env_file(config_dir, cli_name, model)
            if env_file:
                adapter_kwargs["env_file"] = env_file

        adapter = get_adapter(cli_name, model=model, **adapter_kwargs)

        log(f"  Running CLI...")
        run_start = time.monotonic()
        output = await adapter.run(
            prompt=task.prompt,
            cwd=workspace_path,
            timeout=task.timeout,
        )
        run_elapsed = time.monotonic() - run_start

        if output.exit_code == -1:
            log(f"  TIMEOUT after {run_elapsed:.1f}s")
        elif output.exit_code != 0:
            log(f"  CLI exited with code {output.exit_code} ({run_elapsed:.1f}s)")
        else:
            tokens_info = f", {output.tokens} tokens" if output.tokens else ""
            log(f"  CLI finished ({run_elapsed:.1f}s{tokens_info})")

        log(f"  Validating...")
        validator_scores = await run_validator(workspace_path)
        efficiency = score_efficiency(output)

        scores = Scores(
            correctness=validator_scores.get("correctness"),
            completion=validator_scores.get("completion"),
            efficiency=efficiency,
            quality=None,
            instruction_following=None,
        )

        return RunResult(
            task_id=task.id,
            model=model,
            cli=cli_name,
            skill=task.skill,
            scores=scores,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    finally:
        workspace.cleanup()


async def run_matrix(
    tasks: list[TaskConfig],
    cli_names: list[str],
    models: list[str],
    skills_dir: Path | None = None,
    results_dir: Path | None = None,
    config_dir: Path | None = None,
    log: Callable[[str], None] = _default_log,
    **adapter_kwargs,
) -> list[RunResult]:
    results = []
    total = len(tasks) * len(cli_names) * len(models)
    run_num = 0

    for task in tasks:
        for cli_name in cli_names:
            for model in models:
                run_num += 1
                log(f"\n[{run_num}/{total}] {task.id} | {cli_name} | {model}")

                try:
                    result = await run_single_task(
                        task=task,
                        cli_name=cli_name,
                        model=model,
                        skills_dir=skills_dir,
                        config_dir=config_dir,
                        log=log,
                        **adapter_kwargs,
                    )
                    results.append(result)

                    # Print score summary
                    c = result.scores.correctness
                    status = "PASS" if c and c >= 0.5 else "FAIL"
                    log(f"  Result: {status} (correctness={c}, completion={result.scores.completion})")

                    if results_dir:
                        results_dir.mkdir(parents=True, exist_ok=True)
                        filename = f"{result.task_id}_{result.cli}_{result.model}_{result.timestamp}.json"
                        filename = filename.replace(":", "-").replace("/", "-")
                        (results_dir / filename).write_text(result.to_json())

                except Exception as e:
                    log(f"  ERROR: {e}")

    return results
