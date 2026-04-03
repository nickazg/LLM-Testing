from pathlib import Path
from llm_bench.workspace import prepare_workspace


def test_prepare_workspace_copies_template(tmp_path):
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
