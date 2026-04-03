from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from llm_bench.adapters import get_adapter
from llm_bench.models import TaskConfig, RunResult, Scores, OutputFile
from llm_bench.scoring import run_validator, score_efficiency
from llm_bench.workspace import prepare_workspace


def _find_env_file(config_dir: Path, cli_name: str, model: str) -> str | None:
    env_path = config_dir / f"{cli_name}.{model}.env"
    if env_path.exists():
        return str(env_path)
    return None


LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".json": "json",
    ".yaml": "yaml", ".yml": "yaml", ".md": "markdown", ".txt": "text",
    ".sh": "bash", ".html": "html", ".css": "css", ".toml": "toml",
    ".cfg": "ini", ".ini": "ini", ".rs": "rust", ".go": "go", ".cpp": "cpp",
}

# Files/dirs to skip when snapshotting workspace
SKIP_NAMES = {".claude", ".git", "__pycache__", "validate.py", "CLAUDE.md", "AGENTS.md", ".gitkeep", "expected", "kilo.json"}


def _snapshot_files(workspace: Path, max_file_size: int = 50000) -> list[OutputFile]:
    """Capture all files the model created/modified in the workspace."""
    files = []
    for f in sorted(workspace.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(workspace)
        # Skip harness-injected files
        if any(part in SKIP_NAMES for part in rel.parts):
            continue
        try:
            content = f.read_text(errors="replace")
            if len(content) > max_file_size:
                content = content[:max_file_size] + "\n... (truncated)"
        except Exception:
            continue
        lang = LANG_MAP.get(f.suffix.lower(), "")
        files.append(OutputFile(path=str(rel), content=content, language=lang))
    return files


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
            if output.stderr:
                for line in output.stderr.strip().splitlines()[:5]:
                    log(f"    stderr: {line}")
            if output.stdout:
                for line in output.stdout.strip().splitlines()[:5]:
                    log(f"    stdout: {line}")
        else:
            t = output.token_usage
            tokens_info = ""
            if t.total:
                parts = [f"{t.total} tokens"]
                if t.thinking:
                    parts.append(f"{t.thinking} thinking")
                tokens_info = f", {', '.join(parts)}"
            log(f"  CLI finished ({run_elapsed:.1f}s{tokens_info})")
            if not t.total and run_elapsed < 10:
                preview = output.stdout[:200] if output.stdout else "(empty)"
                log(f"  WARNING: Suspiciously fast response. Output preview:")
                for line in preview.splitlines()[:5]:
                    log(f"    {line}")

        log(f"  Validating...")
        validator_scores = await run_validator(workspace_path)
        efficiency = score_efficiency(output)

        # Snapshot files before cleanup
        files = _snapshot_files(workspace_path)
        if files:
            log(f"  Files created: {', '.join(f.path for f in files)}")

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
            prompt=task.prompt,
            raw_output=output.raw_response[:10000],
            conversation=output.conversation,
            files=files,
            tier=task.tier,
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
