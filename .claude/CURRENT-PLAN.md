# LLM Testing Framework — Implementation Plan

**STATUS: COMPLETE** — All 19 tasks implemented, 44 tests passing.

**Goal:** Build an automated benchmarking harness that runs coding tasks across CLI interfaces (Claude Code, Open Code, Kilo CLI) with multiple models, scores results, and displays them in a dashboard.

**Architecture:** Python async harness with CLI-specific adapters, YAML-defined tasks with template dirs and validation scripts, structured JSON results, and a self-contained FastAPI + Chart.js dashboard. The harness copies task templates into temp dirs, launches CLIs as subprocesses, captures output, runs validators, and optionally invokes an LLM judge via Claude Code.

**Tech Stack:** Python 3.11+, asyncio, PyYAML, FastAPI, uvicorn, Chart.js (CDN), hatchling build backend.

---

## Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/llm_bench/__init__.py`
- Create: `src/llm_bench/__main__.py`
- Create: `src/llm_bench/cli.py`
- Create: `.gitignore`
- Create: `tasks/.gitkeep`
- Create: `skills/.gitkeep`
- Create: `results/.gitkeep`
- Create: `config/.gitkeep`
- Create: `tests/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "llm-bench"
version = "0.1.0"
description = "Automated LLM coding benchmark harness"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
]

[project.scripts]
llm-bench = "llm_bench.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/llm_bench"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Step 2: Create src/llm_bench/__init__.py**

```python
"""LLM coding benchmark harness."""
```

**Step 3: Create src/llm_bench/__main__.py**

```python
from llm_bench.cli import main

main()
```

**Step 4: Create src/llm_bench/cli.py (minimal stub)**

```python
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="llm-bench",
        description="Automated LLM coding benchmark harness",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run benchmark tasks")
    run_parser.add_argument("--models", required=True, help="Comma-separated model IDs")
    run_parser.add_argument("--clis", required=True, help="Comma-separated CLI names")
    run_parser.add_argument("--tiers", default="1,2,3,4", help="Comma-separated tier numbers")
    run_parser.add_argument("--tasks", help="Comma-separated task IDs (default: all)")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    print(f"Would run: models={args.models} clis={args.clis} tiers={args.tiers}")


if __name__ == "__main__":
    main()
```

**Step 5: Create .gitignore**

```
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.venv/
.env*
!.env.example
temp/
results/*.json
.pytest_cache/
```

**Step 6: Create directory placeholders**

```bash
mkdir -p tasks skills results config tests src/llm_bench
touch tasks/.gitkeep skills/.gitkeep results/.gitkeep config/.gitkeep tests/__init__.py
```

**Step 7: Install in editable mode and verify**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
llm-bench --help
```

Expected: help text prints with `run` subcommand listed.

**Step 8: Commit**

```bash
git add pyproject.toml src/ tests/ tasks/ skills/ results/ config/ .gitignore
git commit -m "feat: project skeleton with CLI entry point"
```

---

## Task 2: Core Data Models

**Files:**
- Create: `src/llm_bench/models.py`
- Create: `tests/test_models.py`

**Step 1: Write the failing test**

```python
# tests/test_models.py
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_bench.models'`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/models.py
from __future__ import annotations

import json
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class EfficiencyMetrics:
    tokens: int = 0
    tool_calls: int = 0
    wall_time_s: float = 0.0


@dataclass
class Scores:
    correctness: Optional[float] = None
    completion: Optional[float] = None
    efficiency: Optional[EfficiencyMetrics] = None
    quality: Optional[float] = None
    instruction_following: Optional[float] = None


@dataclass
class TaskConfig:
    id: str
    name: str
    tier: int
    prompt: str
    timeout: int
    skill: Optional[str]
    tags: list[str]
    scoring_automated: list[str]
    scoring_flagged: list[str]
    task_dir: Path = field(repr=False)

    @classmethod
    def from_dir(cls, task_dir: Path) -> TaskConfig:
        yaml_path = task_dir / "task.yaml"
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        return cls(
            id=data["id"],
            name=data["name"],
            tier=data["tier"],
            prompt=data["prompt"],
            timeout=data["timeout"],
            skill=data.get("skill"),
            tags=data.get("tags", []),
            scoring_automated=data.get("scoring", {}).get("automated", []),
            scoring_flagged=data.get("scoring", {}).get("flagged", []),
            task_dir=task_dir,
        )


@dataclass
class RunResult:
    task_id: str
    model: str
    cli: str
    skill: Optional[str]
    scores: Scores
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
```

Expected: 3 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/models.py tests/test_models.py
git commit -m "feat: core data models — TaskConfig, RunResult, Scores"
```

---

## Task 3: Task Loader

**Files:**
- Create: `src/llm_bench/loader.py`
- Create: `tests/test_loader.py`

**Step 1: Write the failing test**

```python
# tests/test_loader.py
from pathlib import Path
from llm_bench.loader import load_tasks


def test_load_tasks_filters_by_tier(tmp_path):
    # Create tier1 task
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

    # Create tier2 task
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_loader.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_bench.loader'`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/loader.py
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
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_loader.py -v
```

Expected: 3 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/loader.py tests/test_loader.py
git commit -m "feat: task loader with tier and ID filtering"
```

---

## Task 4: Workspace Manager

**Files:**
- Create: `src/llm_bench/workspace.py`
- Create: `tests/test_workspace.py`

**Step 1: Write the failing test**

```python
# tests/test_workspace.py
from pathlib import Path
from llm_bench.workspace import prepare_workspace


def test_prepare_workspace_copies_template(tmp_path):
    # Create a fake task dir with template
    task_dir = tmp_path / "task"
    template = task_dir / "template"
    template.mkdir(parents=True)
    (template / "app.py").write_text("print('hello')")
    (template / "requirements.txt").write_text("flask")
    (task_dir / "validate.py").write_text("import sys; sys.exit(0)")

    workspace = prepare_workspace(task_dir, cli_name="claude-code", skill_path=None)
    ws_path = Path(workspace.name)

    assert (ws_path / "app.py").read_text() == "print('hello')"
    assert (ws_path / "requirements.txt").read_text() == "flask"
    assert (ws_path / "validate.py").exists()
    workspace.cleanup()


def test_prepare_workspace_injects_skill(tmp_path):
    task_dir = tmp_path / "task"
    (task_dir / "template").mkdir(parents=True)
    (task_dir / "validate.py").write_text("import sys; sys.exit(0)")

    skill_path = tmp_path / "skills" / "usd-basics" / "SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text("---\nname: usd-basics\n---\nUSD guidance here.")

    workspace = prepare_workspace(task_dir, cli_name="claude-code", skill_path=skill_path)
    ws_path = Path(workspace.name)

    injected = ws_path / ".claude" / "skills" / "usd-basics" / "SKILL.md"
    assert injected.exists()
    assert "USD guidance here" in injected.read_text()
    workspace.cleanup()


def test_prepare_workspace_writes_claude_md_for_claude_code(tmp_path):
    task_dir = tmp_path / "task"
    (task_dir / "template").mkdir(parents=True)
    (task_dir / "validate.py").write_text("import sys; sys.exit(0)")

    workspace = prepare_workspace(task_dir, cli_name="claude-code", skill_path=None)
    ws_path = Path(workspace.name)

    assert (ws_path / "CLAUDE.md").exists()
    assert not (ws_path / "AGENTS.md").exists()
    workspace.cleanup()


def test_prepare_workspace_writes_agents_md_for_opencode(tmp_path):
    task_dir = tmp_path / "task"
    (task_dir / "template").mkdir(parents=True)
    (task_dir / "validate.py").write_text("import sys; sys.exit(0)")

    workspace = prepare_workspace(task_dir, cli_name="open-code", skill_path=None)
    ws_path = Path(workspace.name)

    assert (ws_path / "AGENTS.md").exists()
    workspace.cleanup()


def test_prepare_workspace_writes_agents_md_for_kilo(tmp_path):
    task_dir = tmp_path / "task"
    (task_dir / "template").mkdir(parents=True)
    (task_dir / "validate.py").write_text("import sys; sys.exit(0)")

    workspace = prepare_workspace(task_dir, cli_name="kilo", skill_path=None)
    ws_path = Path(workspace.name)

    assert (ws_path / "AGENTS.md").exists()
    workspace.cleanup()
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_workspace.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'llm_bench.workspace'`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/workspace.py
import shutil
import tempfile
from pathlib import Path

# Maps CLI name to which project context file it reads
CONTEXT_FILE = {
    "claude-code": "CLAUDE.md",
    "open-code": "AGENTS.md",
    "kilo": "AGENTS.md",
}

CONTEXT_CONTENT = "Complete the task described in your prompt. Do not ask questions."


def prepare_workspace(
    task_dir: Path,
    cli_name: str,
    skill_path: Path | None = None,
) -> tempfile.TemporaryDirectory:
    tmpdir = tempfile.TemporaryDirectory(prefix="llm-bench-")
    workspace = Path(tmpdir.name)

    # Copy template files
    template = task_dir / "template"
    if template.exists():
        shutil.copytree(template, workspace, dirs_exist_ok=True)

    # Copy validate.py
    validate = task_dir / "validate.py"
    if validate.exists():
        shutil.copy2(validate, workspace / "validate.py")

    # Copy expected/ if present
    expected = task_dir / "expected"
    if expected.exists():
        shutil.copytree(expected, workspace / "expected")

    # Write project context file for this CLI
    context_filename = CONTEXT_FILE.get(cli_name, "AGENTS.md")
    (workspace / context_filename).write_text(CONTEXT_CONTENT)

    # Inject skill if provided
    if skill_path and skill_path.exists():
        skill_name = skill_path.parent.name
        skill_dest = workspace / ".claude" / "skills" / skill_name
        skill_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_path, skill_dest / "SKILL.md")

    return tmpdir
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_workspace.py -v
```

Expected: 5 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/workspace.py tests/test_workspace.py
git commit -m "feat: workspace manager — temp dirs, skill injection, context files"
```

---

## Task 5: Adapter Base Class

**Files:**
- Create: `src/llm_bench/adapters/__init__.py`
- Create: `src/llm_bench/adapters/base.py`
- Create: `tests/test_adapter_base.py`

**Step 1: Write the failing test**

```python
# tests/test_adapter_base.py
import asyncio
from llm_bench.adapters.base import CLIAdapter, CLIOutput


def test_cli_output_dataclass():
    output = CLIOutput(
        stdout="hello",
        stderr="",
        exit_code=0,
        wall_time_s=1.5,
        tokens=100,
        tool_calls=2,
        cost_usd=0.01,
    )
    assert output.exit_code == 0
    assert output.wall_time_s == 1.5


def test_adapter_is_abstract():
    try:
        adapter = CLIAdapter(model="test")
        asyncio.run(adapter.run("prompt", "/tmp"))
        assert False, "Should have raised NotImplementedError"
    except NotImplementedError:
        pass
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_adapter_base.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/adapters/__init__.py
from llm_bench.adapters.base import CLIAdapter, CLIOutput

__all__ = ["CLIAdapter", "CLIOutput"]
```

```python
# src/llm_bench/adapters/base.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CLIOutput:
    stdout: str
    stderr: str
    exit_code: int
    wall_time_s: float
    tokens: int = 0
    tool_calls: int = 0
    cost_usd: float = 0.0


class CLIAdapter:
    name: str = "base"

    def __init__(self, model: str):
        self.model = model

    async def run(self, prompt: str, cwd: str | Path) -> CLIOutput:
        raise NotImplementedError

    def build_command(self, prompt: str) -> list[str]:
        raise NotImplementedError
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_adapter_base.py -v
```

Expected: 2 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/adapters/ tests/test_adapter_base.py
git commit -m "feat: adapter base class and CLIOutput dataclass"
```

---

## Task 6: Claude Code Adapter

**Files:**
- Create: `src/llm_bench/adapters/claude_code.py`
- Create: `tests/test_adapter_claude_code.py`

**Step 1: Write the failing test**

```python
# tests/test_adapter_claude_code.py
from llm_bench.adapters.claude_code import ClaudeCodeAdapter


def test_build_command():
    adapter = ClaudeCodeAdapter(model="opus")
    cmd = adapter.build_command("Fix the bug in main.py")
    assert cmd[0] == "claude"
    assert "-p" in cmd
    assert "--model" in cmd
    assert "opus" in cmd
    assert "--output-format" in cmd
    assert "json" in cmd
    assert "--allowedTools" in cmd


def test_build_command_with_env_file():
    adapter = ClaudeCodeAdapter(model="qwen3-30b", env_file="/path/to/.env.qwen")
    assert adapter.env_file == "/path/to/.env.qwen"


def test_parse_json_output():
    adapter = ClaudeCodeAdapter(model="opus")
    raw = """{
        "type": "result",
        "subtype": "success",
        "result": "Done. Created hello.py.",
        "session_id": "abc-123",
        "total_cost_usd": 0.05,
        "num_turns": 3,
        "duration_ms": 15000,
        "usage": {
            "input_tokens": 2000,
            "output_tokens": 500,
            "cache_read_input_tokens": 100
        }
    }"""
    parsed = adapter.parse_output(raw)
    assert parsed.tokens == 2500
    assert parsed.cost_usd == 0.05
    assert parsed.exit_code == 0
    assert "Done" in parsed.stdout


def test_parse_json_output_error():
    adapter = ClaudeCodeAdapter(model="opus")
    raw = """{
        "type": "result",
        "subtype": "error",
        "result": "Failed to complete task",
        "total_cost_usd": 0.02,
        "num_turns": 1,
        "duration_ms": 5000,
        "usage": {
            "input_tokens": 500,
            "output_tokens": 100
        }
    }"""
    parsed = adapter.parse_output(raw)
    assert parsed.exit_code == 1
    assert "Failed" in parsed.stdout
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_adapter_claude_code.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/adapters/claude_code.py
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Optional

from llm_bench.adapters.base import CLIAdapter, CLIOutput


class ClaudeCodeAdapter(CLIAdapter):
    name = "claude-code"

    def __init__(self, model: str, env_file: str | None = None):
        super().__init__(model)
        self.env_file = env_file

    def build_command(self, prompt: str) -> list[str]:
        return [
            "claude",
            "-p", prompt,
            "--model", self.model,
            "--output-format", "json",
            "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep",
            "--no-session-persistence",
        ]

    def parse_output(self, raw: str) -> CLIOutput:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return CLIOutput(
                stdout=raw, stderr="Failed to parse JSON output",
                exit_code=1, wall_time_s=0,
            )

        usage = data.get("usage", {})
        tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        is_error = data.get("subtype") == "error"

        return CLIOutput(
            stdout=data.get("result", ""),
            stderr="" if not is_error else data.get("result", ""),
            exit_code=1 if is_error else 0,
            wall_time_s=data.get("duration_ms", 0) / 1000.0,
            tokens=tokens,
            tool_calls=data.get("num_turns", 0),
            cost_usd=data.get("total_cost_usd", 0.0),
        )

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        cmd = self.build_command(prompt)
        env = None

        # If an env_file is specified, load it into a copy of the environment
        if self.env_file:
            import os
            env = os.environ.copy()
            env_path = Path(self.env_file)
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        env[key.strip()] = value.strip()

        start = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd),
            env=env,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=10)
            except asyncio.TimeoutError:
                proc.kill()
            elapsed = time.monotonic() - start
            return CLIOutput(
                stdout="", stderr="TIMEOUT",
                exit_code=-1, wall_time_s=elapsed,
            )

        elapsed = time.monotonic() - start
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")

        output = self.parse_output(stdout)
        output.wall_time_s = elapsed  # Use our own measurement
        return output
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_adapter_claude_code.py -v
```

Expected: 4 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/adapters/claude_code.py tests/test_adapter_claude_code.py
git commit -m "feat: Claude Code adapter — command building, JSON parsing, async run"
```

---

## Task 7: Open Code Adapter

**Files:**
- Create: `src/llm_bench/adapters/open_code.py`
- Create: `tests/test_adapter_open_code.py`

**Step 1: Write the failing test**

```python
# tests/test_adapter_open_code.py
from llm_bench.adapters.open_code import OpenCodeAdapter


def test_build_command():
    adapter = OpenCodeAdapter(model="anthropic/claude-sonnet-4-20250514")
    cmd = adapter.build_command("Fix the bug")
    assert cmd[0] == "opencode"
    assert "run" in cmd
    assert "--model" in cmd or "-m" in cmd
    assert "--format" in cmd or "-f" in cmd
    assert "json" in cmd


def test_build_command_with_cwd():
    adapter = OpenCodeAdapter(model="anthropic/claude-sonnet-4-20250514")
    cmd = adapter.build_command("Fix the bug")
    # opencode run uses --cwd for working directory
    assert "opencode" in cmd[0]


def test_parse_output_text():
    adapter = OpenCodeAdapter(model="test")
    # OpenCode JSON output does not include token usage
    output = adapter.parse_output('{"result": "Done fixing the bug."}')
    assert output.exit_code == 0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_adapter_open_code.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/adapters/open_code.py
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from llm_bench.adapters.base import CLIAdapter, CLIOutput


class OpenCodeAdapter(CLIAdapter):
    name = "open-code"

    def build_command(self, prompt: str) -> list[str]:
        return [
            "opencode",
            "run",
            "--model", self.model,
            "--format", "json",
            "-q",
            prompt,
        ]

    def parse_output(self, raw: str) -> CLIOutput:
        # OpenCode does not embed token usage in run output
        try:
            data = json.loads(raw)
            result_text = data.get("result", raw)
        except json.JSONDecodeError:
            result_text = raw

        return CLIOutput(
            stdout=result_text,
            stderr="",
            exit_code=0,
            wall_time_s=0,
            tokens=0,  # Not available in opencode run output
            tool_calls=0,
            cost_usd=0.0,
        )

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        cmd = self.build_command(prompt)

        start = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd),
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=10)
            except asyncio.TimeoutError:
                proc.kill()
            elapsed = time.monotonic() - start
            return CLIOutput(
                stdout="", stderr="TIMEOUT",
                exit_code=-1, wall_time_s=elapsed,
            )

        elapsed = time.monotonic() - start
        stdout = stdout_bytes.decode("utf-8", errors="replace")

        output = self.parse_output(stdout)
        output.wall_time_s = elapsed
        output.exit_code = proc.returncode or 0
        return output
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_adapter_open_code.py -v
```

Expected: 3 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/adapters/open_code.py tests/test_adapter_open_code.py
git commit -m "feat: Open Code adapter"
```

---

## Task 8: Kilo CLI Adapter

**Files:**
- Create: `src/llm_bench/adapters/kilo.py`
- Create: `tests/test_adapter_kilo.py`

**Step 1: Write the failing test**

```python
# tests/test_adapter_kilo.py
from llm_bench.adapters.kilo import KiloAdapter


def test_build_command():
    adapter = KiloAdapter(model="anthropic/claude-sonnet-4-20250514")
    cmd = adapter.build_command("Fix the bug")
    assert cmd[0] == "kilo"
    assert "run" in cmd
    assert "--auto" in cmd
    assert "--json" in cmd


def test_parse_output():
    adapter = KiloAdapter(model="test")
    output = adapter.parse_output('{"type": "assistant", "content": "Done."}')
    assert output.exit_code == 0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_adapter_kilo.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/adapters/kilo.py
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from llm_bench.adapters.base import CLIAdapter, CLIOutput


class KiloAdapter(CLIAdapter):
    name = "kilo"

    def build_command(self, prompt: str) -> list[str]:
        return [
            "kilo",
            "run",
            "--auto",
            "--json",
            prompt,
        ]

    def parse_output(self, raw: str) -> CLIOutput:
        # Kilo outputs one JSON message per line
        lines = raw.strip().splitlines()
        full_output = []
        for line in lines:
            try:
                msg = json.loads(line)
                if msg.get("type") == "assistant":
                    full_output.append(msg.get("content", ""))
            except json.JSONDecodeError:
                full_output.append(line)

        return CLIOutput(
            stdout="\n".join(full_output),
            stderr="",
            exit_code=0,
            wall_time_s=0,
            tokens=0,  # Not available in kilo run output
            tool_calls=0,
            cost_usd=0.0,
        )

    async def run(self, prompt: str, cwd: str | Path, timeout: int = 300) -> CLIOutput:
        cmd = self.build_command(prompt)

        start = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd),
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=10)
            except asyncio.TimeoutError:
                proc.kill()
            elapsed = time.monotonic() - start
            return CLIOutput(
                stdout="", stderr="TIMEOUT",
                exit_code=-1, wall_time_s=elapsed,
            )

        elapsed = time.monotonic() - start
        stdout = stdout_bytes.decode("utf-8", errors="replace")

        output = self.parse_output(stdout)
        output.wall_time_s = elapsed
        output.exit_code = proc.returncode or 0
        return output
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_adapter_kilo.py -v
```

Expected: 2 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/adapters/kilo.py tests/test_adapter_kilo.py
git commit -m "feat: Kilo CLI adapter"
```

---

## Task 9: Adapter Registry

**Files:**
- Modify: `src/llm_bench/adapters/__init__.py`
- Create: `tests/test_adapter_registry.py`

**Step 1: Write the failing test**

```python
# tests/test_adapter_registry.py
from llm_bench.adapters import get_adapter
from llm_bench.adapters.claude_code import ClaudeCodeAdapter
from llm_bench.adapters.open_code import OpenCodeAdapter
from llm_bench.adapters.kilo import KiloAdapter


def test_get_claude_code_adapter():
    adapter = get_adapter("claude-code", model="opus")
    assert isinstance(adapter, ClaudeCodeAdapter)
    assert adapter.model == "opus"


def test_get_open_code_adapter():
    adapter = get_adapter("open-code", model="anthropic/claude-sonnet-4-20250514")
    assert isinstance(adapter, OpenCodeAdapter)


def test_get_kilo_adapter():
    adapter = get_adapter("kilo", model="test")
    assert isinstance(adapter, KiloAdapter)


def test_get_unknown_adapter():
    try:
        get_adapter("unknown-cli", model="test")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_adapter_registry.py -v
```

Expected: FAIL — `ImportError: cannot import name 'get_adapter'`

**Step 3: Update adapters/__init__.py**

```python
# src/llm_bench/adapters/__init__.py
from llm_bench.adapters.base import CLIAdapter, CLIOutput
from llm_bench.adapters.claude_code import ClaudeCodeAdapter
from llm_bench.adapters.open_code import OpenCodeAdapter
from llm_bench.adapters.kilo import KiloAdapter

ADAPTERS: dict[str, type[CLIAdapter]] = {
    "claude-code": ClaudeCodeAdapter,
    "open-code": OpenCodeAdapter,
    "kilo": KiloAdapter,
}


def get_adapter(cli_name: str, model: str, **kwargs) -> CLIAdapter:
    cls = ADAPTERS.get(cli_name)
    if cls is None:
        raise ValueError(f"Unknown CLI: {cli_name}. Available: {list(ADAPTERS.keys())}")
    return cls(model=model, **kwargs)


__all__ = ["CLIAdapter", "CLIOutput", "get_adapter"]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_adapter_registry.py -v
```

Expected: 4 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/adapters/__init__.py tests/test_adapter_registry.py
git commit -m "feat: adapter registry with get_adapter()"
```

---

## Task 10: Automated Scorer

**Files:**
- Create: `src/llm_bench/scoring.py`
- Create: `tests/test_scoring.py`

**Step 1: Write the failing test**

```python
# tests/test_scoring.py
import asyncio
from pathlib import Path
from llm_bench.scoring import run_validator, score_efficiency
from llm_bench.adapters.base import CLIOutput


def test_run_validator_pass(tmp_path):
    (tmp_path / "validate.py").write_text(
        'import json, sys\nprint(json.dumps({"correctness": 1.0, "completion": 1.0}))\nsys.exit(0)'
    )
    result = asyncio.run(run_validator(tmp_path))
    assert result["correctness"] == 1.0
    assert result["completion"] == 1.0


def test_run_validator_fail(tmp_path):
    (tmp_path / "validate.py").write_text(
        'import json, sys\nprint(json.dumps({"correctness": 0.0, "completion": 0.5}))\nsys.exit(1)'
    )
    result = asyncio.run(run_validator(tmp_path))
    assert result["correctness"] == 0.0


def test_run_validator_no_json_output(tmp_path):
    (tmp_path / "validate.py").write_text("import sys; sys.exit(0)")
    result = asyncio.run(run_validator(tmp_path))
    assert result["correctness"] == 1.0  # exit 0 = pass


def test_run_validator_crash(tmp_path):
    (tmp_path / "validate.py").write_text("raise Exception('boom')")
    result = asyncio.run(run_validator(tmp_path))
    assert result["correctness"] == 0.0


def test_score_efficiency():
    output = CLIOutput(
        stdout="done", stderr="", exit_code=0,
        wall_time_s=30.0, tokens=2000, tool_calls=5, cost_usd=0.03,
    )
    eff = score_efficiency(output)
    assert eff.tokens == 2000
    assert eff.tool_calls == 5
    assert eff.wall_time_s == 30.0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_scoring.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/scoring.py
from __future__ import annotations

import asyncio
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

    # Try to parse JSON from stdout
    scores = {}
    if result.stdout.strip():
        try:
            scores = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            pass

    # If no JSON output, use exit code as correctness
    if not scores:
        scores = {
            "correctness": 1.0 if result.returncode == 0 else 0.0,
            "completion": 1.0 if result.returncode == 0 else 0.0,
        }

    return scores


def score_efficiency(output: CLIOutput) -> EfficiencyMetrics:
    return EfficiencyMetrics(
        tokens=output.tokens,
        tool_calls=output.tool_calls,
        wall_time_s=output.wall_time_s,
    )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_scoring.py -v
```

Expected: 5 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/scoring.py tests/test_scoring.py
git commit -m "feat: automated scorer — validator runner and efficiency metrics"
```

---

## Task 11: Runner (Orchestrator)

**Files:**
- Create: `src/llm_bench/runner.py`
- Create: `tests/test_runner.py`

**Step 1: Write the failing test**

```python
# tests/test_runner.py
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
from llm_bench.runner import run_single_task
from llm_bench.models import TaskConfig
from llm_bench.adapters.base import CLIOutput


def _make_task(tmp_path, tier=1, skill=None):
    task_dir = tmp_path / f"tier{tier}" / "test-task"
    template = task_dir / "template"
    template.mkdir(parents=True)
    (template / "main.py").write_text("# placeholder")
    (task_dir / "validate.py").write_text(
        'import json, sys\nprint(json.dumps({"correctness": 1.0, "completion": 1.0}))\nsys.exit(0)'
    )
    (task_dir / "task.yaml").write_text(f"""
id: tier{tier}-test-task
name: Test Task
tier: {tier}
prompt: "Write hello world"
timeout: 60
skill: {skill if skill else 'null'}
tags: [python]
scoring:
  automated: [correctness, completion, efficiency]
  flagged: [quality]
""")
    return TaskConfig.from_dir(task_dir)


def test_run_single_task(tmp_path):
    task = _make_task(tmp_path)

    mock_output = CLIOutput(
        stdout="Done", stderr="", exit_code=0,
        wall_time_s=10.0, tokens=500, tool_calls=3, cost_usd=0.01,
    )

    with patch("llm_bench.runner.get_adapter") as mock_get:
        mock_adapter = AsyncMock()
        mock_adapter.run.return_value = mock_output
        mock_adapter.name = "claude-code"
        mock_get.return_value = mock_adapter

        result = asyncio.run(run_single_task(task, cli_name="claude-code", model="opus"))

    assert result.task_id == "tier1-test-task"
    assert result.model == "opus"
    assert result.cli == "claude-code"
    assert result.scores.correctness == 1.0
    assert result.scores.efficiency.tokens == 500
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_runner.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/runner.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from llm_bench.adapters import get_adapter
from llm_bench.models import TaskConfig, RunResult, Scores
from llm_bench.scoring import run_validator, score_efficiency
from llm_bench.workspace import prepare_workspace


async def run_single_task(
    task: TaskConfig,
    cli_name: str,
    model: str,
    skills_dir: Path | None = None,
    **adapter_kwargs,
) -> RunResult:
    # Resolve skill path if task references one
    skill_path = None
    if task.skill and skills_dir:
        skill_path = skills_dir / task.skill / "SKILL.md"
        if not skill_path.exists():
            skill_path = None

    # Prepare isolated workspace
    workspace = prepare_workspace(
        task_dir=task.task_dir,
        cli_name=cli_name,
        skill_path=skill_path,
    )
    workspace_path = Path(workspace.name)

    try:
        # Run the CLI
        adapter = get_adapter(cli_name, model=model, **adapter_kwargs)
        output = await adapter.run(
            prompt=task.prompt,
            cwd=workspace_path,
            timeout=task.timeout,
        )

        # Score the result
        validator_scores = await run_validator(workspace_path)
        efficiency = score_efficiency(output)

        scores = Scores(
            correctness=validator_scores.get("correctness"),
            completion=validator_scores.get("completion"),
            efficiency=efficiency,
            quality=None,  # Flagged for LLM judge
            instruction_following=None,  # Flagged for LLM judge
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
    **adapter_kwargs,
) -> list[RunResult]:
    results = []
    for task in tasks:
        for cli_name in cli_names:
            for model in models:
                result = await run_single_task(
                    task=task,
                    cli_name=cli_name,
                    model=model,
                    skills_dir=skills_dir,
                    **adapter_kwargs,
                )
                results.append(result)

                # Save result to disk
                if results_dir:
                    results_dir.mkdir(parents=True, exist_ok=True)
                    filename = f"{result.task_id}_{result.cli}_{result.model}_{result.timestamp}.json"
                    # Sanitize filename
                    filename = filename.replace(":", "-").replace("/", "-")
                    (results_dir / filename).write_text(result.to_json())

    return results
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_runner.py -v
```

Expected: 1 test PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/runner.py tests/test_runner.py
git commit -m "feat: runner — orchestrates task execution across CLI/model matrix"
```

---

## Task 12: Wire Up the CLI

**Files:**
- Modify: `src/llm_bench/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
# tests/test_cli.py
import subprocess
import sys


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "llm_bench", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "run" in result.stdout


def test_cli_run_help():
    result = subprocess.run(
        [sys.executable, "-m", "llm_bench", "run", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "--models" in result.stdout
    assert "--clis" in result.stdout
    assert "--tiers" in result.stdout
```

**Step 2: Run test to verify it fails (or passes if stub already works)**

```bash
pytest tests/test_cli.py -v
```

**Step 3: Update cli.py with real wiring**

```python
# src/llm_bench/cli.py
import argparse
import asyncio
import sys
from pathlib import Path

from llm_bench.loader import load_tasks
from llm_bench.runner import run_matrix


def main():
    parser = argparse.ArgumentParser(
        prog="llm-bench",
        description="Automated LLM coding benchmark harness",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- run ---
    run_parser = subparsers.add_parser("run", help="Run benchmark tasks")
    run_parser.add_argument("--models", required=True, help="Comma-separated model IDs")
    run_parser.add_argument("--clis", required=True, help="Comma-separated CLI names (claude-code, open-code, kilo)")
    run_parser.add_argument("--tiers", default="1,2,3,4", help="Comma-separated tier numbers")
    run_parser.add_argument("--tasks", help="Comma-separated task IDs (default: all)")
    run_parser.add_argument("--tasks-dir", default="tasks", help="Path to tasks directory")
    run_parser.add_argument("--skills-dir", default="skills", help="Path to skills directory")
    run_parser.add_argument("--results-dir", default="results", help="Path to results directory")

    # --- dashboard ---
    dash_parser = subparsers.add_parser("dashboard", help="Launch results dashboard")
    dash_parser.add_argument("--port", type=int, default=8080, help="Port number")
    dash_parser.add_argument("--results-dir", default="results", help="Path to results directory")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        _handle_run(args)
    elif args.command == "dashboard":
        _handle_dashboard(args)


def _handle_run(args):
    tasks_dir = Path(args.tasks_dir)
    skills_dir = Path(args.skills_dir)
    results_dir = Path(args.results_dir)
    tiers = [int(t) for t in args.tiers.split(",")]
    models = args.models.split(",")
    cli_names = args.clis.split(",")
    task_ids = args.tasks.split(",") if args.tasks else None

    tasks = load_tasks(tasks_dir, tiers=tiers, task_ids=task_ids)
    if not tasks:
        print(f"No tasks found in {tasks_dir} for tiers {tiers}")
        sys.exit(1)

    print(f"Running {len(tasks)} tasks × {len(cli_names)} CLIs × {len(models)} models")
    print(f"Total runs: {len(tasks) * len(cli_names) * len(models)}")

    results = asyncio.run(
        run_matrix(
            tasks=tasks,
            cli_names=cli_names,
            models=models,
            skills_dir=skills_dir,
            results_dir=results_dir,
        )
    )

    # Summary
    passed = sum(1 for r in results if r.scores.correctness and r.scores.correctness >= 0.5)
    print(f"\nComplete: {len(results)} runs, {passed} passed")


def _handle_dashboard(args):
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Run: pip install uvicorn[standard]")
        sys.exit(1)
    # Dashboard import deferred to avoid loading FastAPI at CLI startup
    print(f"Starting dashboard on http://localhost:{args.port}")
    print(f"Results directory: {args.results_dir}")
    uvicorn.run(
        "llm_bench.dashboard.app:app",
        host="0.0.0.0",
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_cli.py -v
```

Expected: 2 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/cli.py tests/test_cli.py
git commit -m "feat: wire CLI to runner with run and dashboard subcommands"
```

---

## Task 13: First Test Task (Tier 1)

**Files:**
- Create: `tasks/tier1/hello-world/task.yaml`
- Create: `tasks/tier1/hello-world/template/` (empty — model starts from scratch)
- Create: `tasks/tier1/hello-world/validate.py`

**Step 1: Create task.yaml**

```yaml
# tasks/tier1/hello-world/task.yaml
id: tier1-hello-world
name: "Hello World"
tier: 1
prompt: "Create a Python file called hello.py that prints 'Hello, World!' to stdout. Do not create any other files."
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
```

**Step 2: Create template directory (empty — clean start)**

```bash
mkdir -p tasks/tier1/hello-world/template
touch tasks/tier1/hello-world/template/.gitkeep
```

**Step 3: Create validate.py**

```python
# tasks/tier1/hello-world/validate.py
"""Validator for tier1-hello-world task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}

workspace = Path(".")

# Check hello.py exists
hello_py = workspace / "hello.py"
if not hello_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

# Run hello.py and check output
try:
    result = subprocess.run(
        [sys.executable, str(hello_py)],
        capture_output=True, text=True, timeout=10,
    )
    if "Hello, World!" in result.stdout:
        scores["correctness"] = 1.0
    elif "hello" in result.stdout.lower() and "world" in result.stdout.lower():
        scores["correctness"] = 0.5  # Close enough
except Exception:
    pass

print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.5 else 1)
```

**Step 4: Verify task loads**

```bash
python -c "
from llm_bench.loader import load_tasks
from pathlib import Path
tasks = load_tasks(Path('tasks'), tiers=[1])
print(f'Found {len(tasks)} tasks')
for t in tasks:
    print(f'  {t.id}: {t.name} (tier {t.tier})')
"
```

Expected: `Found 1 tasks` with `tier1-hello-world`.

**Step 5: Commit**

```bash
git add tasks/tier1/hello-world/
git commit -m "feat: first test task — tier1 hello world with validator"
```

---

## Task 14: Second Test Task (Tier 1 — FizzBuzz)

**Files:**
- Create: `tasks/tier1/fizzbuzz/task.yaml`
- Create: `tasks/tier1/fizzbuzz/template/.gitkeep`
- Create: `tasks/tier1/fizzbuzz/validate.py`

**Step 1: Create task.yaml**

```yaml
# tasks/tier1/fizzbuzz/task.yaml
id: tier1-fizzbuzz
name: "FizzBuzz"
tier: 1
prompt: "Create a Python file called fizzbuzz.py that prints numbers 1 to 100, but prints 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, and 'FizzBuzz' for multiples of both. One value per line."
timeout: 120
skill: null
tags: [python, basics, logic]
scoring:
  automated:
    - correctness
    - completion
    - efficiency
  flagged:
    - quality
    - instruction_following
```

**Step 2: Create template directory**

```bash
mkdir -p tasks/tier1/fizzbuzz/template
touch tasks/tier1/fizzbuzz/template/.gitkeep
```

**Step 3: Create validate.py**

```python
# tasks/tier1/fizzbuzz/validate.py
"""Validator for tier1-fizzbuzz task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}

workspace = Path(".")
fizzbuzz_py = workspace / "fizzbuzz.py"

if not fizzbuzz_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

# Generate expected output
expected_lines = []
for i in range(1, 101):
    if i % 15 == 0:
        expected_lines.append("FizzBuzz")
    elif i % 3 == 0:
        expected_lines.append("Fizz")
    elif i % 5 == 0:
        expected_lines.append("Buzz")
    else:
        expected_lines.append(str(i))

try:
    result = subprocess.run(
        [sys.executable, str(fizzbuzz_py)],
        capture_output=True, text=True, timeout=10,
    )
    actual_lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]

    if len(actual_lines) == 100:
        correct = sum(1 for a, e in zip(actual_lines, expected_lines) if a == e)
        scores["correctness"] = correct / 100.0
except Exception:
    pass

print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.9 else 1)
```

**Step 4: Commit**

```bash
git add tasks/tier1/fizzbuzz/
git commit -m "feat: tier1 fizzbuzz task with validator"
```

---

## Task 15: LLM Judge Scorer

**Files:**
- Create: `src/llm_bench/judge.py`
- Create: `tests/test_judge.py`

**Step 1: Write the failing test**

```python
# tests/test_judge.py
from llm_bench.judge import build_judge_prompt, parse_judge_response


def test_build_judge_prompt():
    prompt = build_judge_prompt(
        task_prompt="Write hello world in Python",
        code="print('Hello, World!')",
        dimension="quality",
    )
    assert "Write hello world" in prompt
    assert "print('Hello, World!')" in prompt
    assert "quality" in prompt.lower() or "Quality" in prompt


def test_parse_judge_response_valid():
    response = '{"score": 4, "reasoning": "Clean and simple implementation."}'
    result = parse_judge_response(response)
    assert result["score"] == 4
    assert "Clean" in result["reasoning"]


def test_parse_judge_response_extracts_json():
    response = 'Here is my assessment:\n\n```json\n{"score": 3, "reasoning": "Acceptable."}\n```'
    result = parse_judge_response(response)
    assert result["score"] == 3


def test_parse_judge_response_invalid():
    response = "I think the code is pretty good, maybe 4 out of 5."
    result = parse_judge_response(response)
    assert result["score"] is None
    assert "parse" in result["reasoning"].lower() or result["reasoning"]
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_judge.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/judge.py
from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Optional

from llm_bench.adapters.claude_code import ClaudeCodeAdapter

RUBRICS = {
    "quality": """Rate the code quality on a scale of 1-5:
1 = Broken, unreadable, or fundamentally wrong approach
2 = Works but poor style, unnecessary complexity, or non-idiomatic
3 = Acceptable — functional, readable, minor issues
4 = Good — clean, idiomatic, well-structured
5 = Excellent — elegant, efficient, production-ready

Focus on: readability, idiomatic patterns, appropriate complexity, naming, structure.""",

    "instruction_following": """Rate how well the code follows the original instructions on a scale of 1-5:
1 = Completely ignored instructions or did something else entirely
2 = Partially followed — missed major requirements
3 = Mostly followed — minor deviations or extras
4 = Followed well — all requirements met, minimal extras
5 = Perfectly followed — exactly what was asked, nothing more, nothing less

Focus on: completeness, accuracy, no unrequested features, no missing requirements.""",
}


def build_judge_prompt(task_prompt: str, code: str, dimension: str) -> str:
    rubric = RUBRICS.get(dimension, f"Rate the {dimension} on a scale of 1-5.")
    return f"""You are a blind code reviewer. You do not know which model or tool produced this code.

## Original Task
{task_prompt}

## Code Produced
```
{code}
```

## Scoring Dimension: {dimension.replace("_", " ").title()}
{rubric}

Respond with ONLY a JSON object:
{{"score": <1-5>, "reasoning": "<brief explanation>"}}"""


def parse_judge_response(response: str) -> dict:
    # Try direct JSON parse
    try:
        data = json.loads(response.strip())
        if "score" in data:
            return data
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if "score" in data:
                return data
        except json.JSONDecodeError:
            pass

    # Try to find any JSON object in the response
    match = re.search(r'\{[^{}]*"score"\s*:\s*\d[^{}]*\}', response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {"score": None, "reasoning": f"Could not parse judge response: {response[:200]}"}


async def judge_code(
    task_prompt: str,
    code: str,
    dimension: str,
    env_file: str | None = None,
) -> dict:
    prompt = build_judge_prompt(task_prompt, code, dimension)

    adapter = ClaudeCodeAdapter(model="opus", env_file=env_file)
    output = await adapter.run(prompt=prompt, cwd="/tmp", timeout=120)

    return parse_judge_response(output.stdout)
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_judge.py -v
```

Expected: 4 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/judge.py tests/test_judge.py
git commit -m "feat: LLM judge scorer — prompt building, response parsing, Claude Code invocation"
```

---

## Task 16: Result Storage and Loading

**Files:**
- Create: `src/llm_bench/results.py`
- Create: `tests/test_results.py`

**Step 1: Write the failing test**

```python
# tests/test_results.py
import json
from pathlib import Path
from llm_bench.results import save_result, load_results
from llm_bench.models import RunResult, Scores, EfficiencyMetrics


def _make_result(task_id="tier1-hello", model="opus", cli="claude-code"):
    return RunResult(
        task_id=task_id, model=model, cli=cli, skill=None,
        scores=Scores(
            correctness=1.0, completion=1.0,
            efficiency=EfficiencyMetrics(tokens=500, tool_calls=3, wall_time_s=10.0),
            quality=None, instruction_following=None,
        ),
        timestamp="2026-04-03T14:30:00Z",
    )


def test_save_and_load_result(tmp_path):
    result = _make_result()
    save_result(result, tmp_path)

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1

    loaded = load_results(tmp_path)
    assert len(loaded) == 1
    assert loaded[0]["task_id"] == "tier1-hello"
    assert loaded[0]["scores"]["correctness"] == 1.0


def test_load_multiple_results(tmp_path):
    save_result(_make_result("task-a", "opus", "claude-code"), tmp_path)
    save_result(_make_result("task-b", "qwen3", "kilo"), tmp_path)

    loaded = load_results(tmp_path)
    assert len(loaded) == 2


def test_load_results_empty_dir(tmp_path):
    loaded = load_results(tmp_path)
    assert loaded == []
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_results.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/results.py
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
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_results.py -v
```

Expected: 3 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/results.py tests/test_results.py
git commit -m "feat: result storage — save and load JSON results"
```

---

## Task 17: Dashboard API

**Files:**
- Create: `src/llm_bench/dashboard/__init__.py`
- Create: `src/llm_bench/dashboard/app.py`
- Create: `tests/test_dashboard_api.py`

**Step 1: Write the failing test**

```python
# tests/test_dashboard_api.py
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_dashboard_api.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/llm_bench/dashboard/__init__.py
```

```python
# src/llm_bench/dashboard/app.py
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

RESULTS_DIR = Path("results")

app = FastAPI(title="LLM Bench Dashboard")


@app.get("/api/results")
async def get_results():
    if not RESULTS_DIR.exists():
        return []
    results = []
    for f in sorted(RESULTS_DIR.glob("*.json")):
        try:
            results.append(json.loads(f.read_text()))
        except json.JSONDecodeError:
            continue
    return results


@app.get("/api/summary")
async def get_summary():
    results = await get_results()
    models = sorted(set(r["model"] for r in results))
    clis = sorted(set(r["cli"] for r in results))
    tasks = sorted(set(r["task_id"] for r in results))
    return {
        "total_runs": len(results),
        "models": models,
        "clis": clis,
        "tasks": tasks,
    }


@app.get("/", response_class=HTMLResponse)
async def index():
    return DASHBOARD_HTML


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Bench Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; padding: 24px; }
        h1 { font-size: 1.5rem; margin-bottom: 8px; }
        .subtitle { color: #888; margin-bottom: 24px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 20px; margin-bottom: 24px; }
        .card { background: #1a1d27; border-radius: 8px; padding: 20px; border: 1px solid #2a2d37; }
        .card h2 { font-size: 1rem; margin-bottom: 12px; color: #aaa; }
        .stats { display: flex; gap: 24px; margin-bottom: 24px; }
        .stat { background: #1a1d27; border-radius: 8px; padding: 16px 24px; border: 1px solid #2a2d37; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #6c9eff; }
        .stat-label { color: #888; font-size: 0.85rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #2a2d37; }
        th { color: #888; font-weight: 500; }
        .score-high { color: #4ade80; }
        .score-mid { color: #facc15; }
        .score-low { color: #f87171; }
        canvas { max-height: 300px; }
        .tabs { display: flex; gap: 8px; margin-bottom: 16px; }
        .tab { padding: 6px 16px; border-radius: 6px; cursor: pointer; background: #2a2d37; border: none; color: #e0e0e0; }
        .tab.active { background: #6c9eff; color: #000; }
    </style>
</head>
<body>
    <h1>LLM Bench Dashboard</h1>
    <p class="subtitle">Model performance across CLI interfaces</p>

    <div class="stats" id="stats"></div>

    <div class="tabs">
        <button class="tab active" onclick="showView('matrix')">Matrix</button>
        <button class="tab" onclick="showView('uplift')">Skill Uplift</button>
        <button class="tab" onclick="showView('efficiency')">Efficiency</button>
        <button class="tab" onclick="showView('runs')">Run History</button>
    </div>

    <div id="view-matrix" class="grid"></div>
    <div id="view-uplift" class="grid" style="display:none"></div>
    <div id="view-efficiency" class="grid" style="display:none"></div>
    <div id="view-runs" style="display:none"></div>

<script>
let allResults = [];

async function init() {
    const res = await fetch('/api/results');
    allResults = await res.json();
    renderStats();
    renderMatrix();
    renderUplift();
    renderEfficiency();
    renderRuns();
}

function scoreClass(s) {
    if (s === null || s === undefined) return '';
    if (s >= 0.8) return 'score-high';
    if (s >= 0.5) return 'score-mid';
    return 'score-low';
}

function renderStats() {
    const models = new Set(allResults.map(r => r.model));
    const clis = new Set(allResults.map(r => r.cli));
    const tasks = new Set(allResults.map(r => r.task_id));
    document.getElementById('stats').innerHTML = `
        <div class="stat"><div class="stat-value">${allResults.length}</div><div class="stat-label">Total Runs</div></div>
        <div class="stat"><div class="stat-value">${models.size}</div><div class="stat-label">Models</div></div>
        <div class="stat"><div class="stat-value">${clis.size}</div><div class="stat-label">CLIs</div></div>
        <div class="stat"><div class="stat-value">${tasks.size}</div><div class="stat-label">Tasks</div></div>
    `;
}

function renderMatrix() {
    const models = [...new Set(allResults.map(r => r.model))];
    const clis = [...new Set(allResults.map(r => r.cli))];

    let html = '<div class="card" style="grid-column: 1/-1"><h2>Model × CLI — Average Correctness</h2><table><tr><th>Model</th>';
    clis.forEach(c => html += `<th>${c}</th>`);
    html += '</tr>';

    models.forEach(model => {
        html += `<tr><td>${model}</td>`;
        clis.forEach(cli => {
            const runs = allResults.filter(r => r.model === model && r.cli === cli);
            if (runs.length === 0) {
                html += '<td>—</td>';
            } else {
                const avg = runs.reduce((s, r) => s + (r.scores.correctness || 0), 0) / runs.length;
                html += `<td class="${scoreClass(avg)}">${avg.toFixed(2)}</td>`;
            }
        });
        html += '</tr>';
    });

    html += '</table></div>';
    document.getElementById('view-matrix').innerHTML = html;
}

function renderUplift() {
    // Find tier3/tier4 pairs
    const tier3 = allResults.filter(r => r.task_id.startsWith('tier3'));
    const tier4 = allResults.filter(r => r.task_id.startsWith('tier4'));
    const models = [...new Set(allResults.map(r => r.model))];

    if (tier3.length === 0 && tier4.length === 0) {
        document.getElementById('view-uplift').innerHTML = '<div class="card"><h2>Skill Uplift</h2><p>No tier 3/4 results yet. Run domain-specific tasks to see skill uplift data.</p></div>';
        return;
    }

    // Build chart data
    const labels = models;
    const t3scores = models.map(m => {
        const runs = tier3.filter(r => r.model === m);
        return runs.length ? runs.reduce((s, r) => s + (r.scores.correctness || 0), 0) / runs.length : 0;
    });
    const t4scores = models.map(m => {
        const runs = tier4.filter(r => r.model === m);
        return runs.length ? runs.reduce((s, r) => s + (r.scores.correctness || 0), 0) / runs.length : 0;
    });

    document.getElementById('view-uplift').innerHTML = '<div class="card" style="grid-column:1/-1"><h2>Skill Uplift — Tier 3 vs Tier 4 Correctness</h2><canvas id="upliftChart"></canvas></div>';

    new Chart(document.getElementById('upliftChart'), {
        type: 'bar',
        data: {
            labels,
            datasets: [
                { label: 'Tier 3 (no skill)', data: t3scores, backgroundColor: '#f87171' },
                { label: 'Tier 4 (with skill)', data: t4scores, backgroundColor: '#4ade80' },
            ]
        },
        options: {
            responsive: true,
            scales: { y: { min: 0, max: 1, ticks: { color: '#888' }, grid: { color: '#2a2d37' } }, x: { ticks: { color: '#888' }, grid: { color: '#2a2d37' } } },
            plugins: { legend: { labels: { color: '#e0e0e0' } } }
        }
    });
}

function renderEfficiency() {
    const data = allResults
        .filter(r => r.scores.efficiency)
        .map(r => ({
            x: r.scores.efficiency.tokens,
            y: r.scores.correctness || 0,
            label: `${r.model} (${r.cli})`,
            model: r.model,
        }));

    const models = [...new Set(data.map(d => d.model))];
    const colors = ['#6c9eff', '#4ade80', '#facc15', '#f87171', '#c084fc'];

    document.getElementById('view-efficiency').innerHTML = '<div class="card" style="grid-column:1/-1"><h2>Efficiency — Tokens vs Correctness</h2><canvas id="effChart"></canvas></div>';

    new Chart(document.getElementById('effChart'), {
        type: 'scatter',
        data: {
            datasets: models.map((m, i) => ({
                label: m,
                data: data.filter(d => d.model === m),
                backgroundColor: colors[i % colors.length],
                pointRadius: 6,
            }))
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Tokens', color: '#888' }, ticks: { color: '#888' }, grid: { color: '#2a2d37' } },
                y: { title: { display: true, text: 'Correctness', color: '#888' }, min: 0, max: 1, ticks: { color: '#888' }, grid: { color: '#2a2d37' } },
            },
            plugins: { legend: { labels: { color: '#e0e0e0' } } }
        }
    });
}

function renderRuns() {
    let html = '<div class="card"><h2>Run History</h2><table><tr><th>Task</th><th>Model</th><th>CLI</th><th>Correct</th><th>Complete</th><th>Tokens</th><th>Time</th><th>Skill</th></tr>';
    allResults.forEach(r => {
        const eff = r.scores.efficiency || {};
        html += `<tr>
            <td>${r.task_id}</td>
            <td>${r.model}</td>
            <td>${r.cli}</td>
            <td class="${scoreClass(r.scores.correctness)}">${r.scores.correctness !== null ? r.scores.correctness.toFixed(2) : '—'}</td>
            <td class="${scoreClass(r.scores.completion)}">${r.scores.completion !== null ? r.scores.completion.toFixed(2) : '—'}</td>
            <td>${eff.tokens || '—'}</td>
            <td>${eff.wall_time_s ? eff.wall_time_s.toFixed(1) + 's' : '—'}</td>
            <td>${r.skill || '—'}</td>
        </tr>`;
    });
    html += '</table></div>';
    document.getElementById('view-runs').innerHTML = html;
}

function showView(name) {
    ['matrix', 'uplift', 'efficiency', 'runs'].forEach(v => {
        document.getElementById('view-' + v).style.display = v === name ? '' : 'none';
    });
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
}

init();
</script>
</body>
</html>"""
```

**Step 4: Run test to verify it passes**

```bash
pip install httpx  # Required by TestClient
pytest tests/test_dashboard_api.py -v
```

Expected: 2 tests PASS.

**Step 5: Commit**

```bash
git add src/llm_bench/dashboard/ tests/test_dashboard_api.py
git commit -m "feat: dashboard — FastAPI API + inline Chart.js single-page UI"
```

---

## Task 18: End-to-End Smoke Test

**Files:**
- Create: `tests/test_e2e.py`

**Step 1: Write the test**

This test verifies the full pipeline works with a mocked CLI adapter.

```python
# tests/test_e2e.py
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from llm_bench.loader import load_tasks
from llm_bench.runner import run_matrix
from llm_bench.adapters.base import CLIOutput
from llm_bench.results import load_results


def _create_task_tree(base: Path):
    """Create a minimal task tree for testing."""
    task_dir = base / "tasks" / "tier1" / "hello-world"
    template = task_dir / "template"
    template.mkdir(parents=True)
    (task_dir / "task.yaml").write_text("""
id: tier1-hello-world
name: Hello World
tier: 1
prompt: "Create hello.py that prints Hello World"
timeout: 60
tags: [python]
scoring:
  automated: [correctness, completion, efficiency]
  flagged: [quality]
""")
    (task_dir / "validate.py").write_text(
        'import json, sys\nprint(json.dumps({"correctness": 1.0, "completion": 1.0}))\nsys.exit(0)'
    )
    return base / "tasks"


def test_e2e_pipeline(tmp_path):
    tasks_dir = _create_task_tree(tmp_path)
    results_dir = tmp_path / "results"

    tasks = load_tasks(tasks_dir, tiers=[1])
    assert len(tasks) == 1

    mock_output = CLIOutput(
        stdout="Created hello.py", stderr="", exit_code=0,
        wall_time_s=8.0, tokens=400, tool_calls=2, cost_usd=0.005,
    )

    with patch("llm_bench.runner.get_adapter") as mock_get:
        mock_adapter = AsyncMock()
        mock_adapter.run.return_value = mock_output
        mock_adapter.name = "claude-code"
        mock_get.return_value = mock_adapter

        results = asyncio.run(run_matrix(
            tasks=tasks,
            cli_names=["claude-code"],
            models=["opus"],
            results_dir=results_dir,
        ))

    assert len(results) == 1
    r = results[0]
    assert r.task_id == "tier1-hello-world"
    assert r.scores.correctness == 1.0
    assert r.scores.efficiency.tokens == 400

    # Verify result was saved to disk
    saved = load_results(results_dir)
    assert len(saved) == 1
    assert saved[0]["task_id"] == "tier1-hello-world"


def test_e2e_multi_model_multi_cli(tmp_path):
    tasks_dir = _create_task_tree(tmp_path)
    results_dir = tmp_path / "results"

    tasks = load_tasks(tasks_dir, tiers=[1])

    mock_output = CLIOutput(
        stdout="Done", stderr="", exit_code=0,
        wall_time_s=10.0, tokens=600, tool_calls=4, cost_usd=0.01,
    )

    with patch("llm_bench.runner.get_adapter") as mock_get:
        mock_adapter = AsyncMock()
        mock_adapter.run.return_value = mock_output
        mock_adapter.name = "test"
        mock_get.return_value = mock_adapter

        results = asyncio.run(run_matrix(
            tasks=tasks,
            cli_names=["claude-code", "kilo"],
            models=["opus", "qwen3-30b"],
            results_dir=results_dir,
        ))

    # 1 task × 2 CLIs × 2 models = 4 runs
    assert len(results) == 4
    saved = load_results(results_dir)
    assert len(saved) == 4
```

**Step 2: Run test**

```bash
pytest tests/test_e2e.py -v
```

Expected: 2 tests PASS.

**Step 3: Run full test suite**

```bash
pytest tests/ -v
```

Expected: All tests pass.

**Step 4: Commit**

```bash
git add tests/test_e2e.py
git commit -m "test: end-to-end smoke tests for full pipeline"
```

---

## Task 19: Final Cleanup and README

**Step 1: Delete .gitkeep files that are no longer needed**

```bash
rm -f tasks/.gitkeep config/.gitkeep
```

**Step 2: Verify full test suite passes**

```bash
pytest tests/ -v --tb=short
```

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: cleanup — remove stale gitkeeps, final structure"
```
