import shutil
import tempfile
from pathlib import Path

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

    template = task_dir / "template"
    if template.exists():
        shutil.copytree(template, workspace, dirs_exist_ok=True)

    validate = task_dir / "validate.py"
    if validate.exists():
        shutil.copy2(validate, workspace / "validate.py")

    expected = task_dir / "expected"
    if expected.exists():
        shutil.copytree(expected, workspace / "expected")

    context_filename = CONTEXT_FILE.get(cli_name, "AGENTS.md")
    (workspace / context_filename).write_text(CONTEXT_CONTENT)

    if skill_path and skill_path.exists():
        skill_name = skill_path.parent.name
        skill_dest = workspace / ".claude" / "skills" / skill_name
        skill_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_path, skill_dest / "SKILL.md")

    return tmpdir
