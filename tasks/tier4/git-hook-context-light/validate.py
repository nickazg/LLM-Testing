"""Validator for tier4-git-hook-context-light — checks top 3 org rules."""
import json
import subprocess
import sys
import os
import tempfile
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
hook = workspace / "pre-commit"

if not hook.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0
tests_passed = 0
total_tests = 5


def run_hook_in_repo(staged_files: dict[str, str | bytes], expect_fail: bool) -> bool:
    """Create a temp git repo, stage files, run the hook, check result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        subprocess.run(["git", "init"], cwd=tmp, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp, capture_output=True)
        (tmp / "README.md").write_text("init")
        subprocess.run(["git", "add", "README.md"], cwd=tmp, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp, capture_output=True)

        for name, content in staged_files.items():
            fpath = tmp / name
            fpath.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                fpath.write_bytes(content)
            else:
                fpath.write_text(content)
            subprocess.run(["git", "add", name], cwd=tmp, capture_output=True)

        hook_dest = tmp / ".git" / "hooks" / "pre-commit"
        hook_dest.write_text(hook.read_text())
        os.chmod(hook_dest, 0o755)

        result = subprocess.run(
            ["bash", str(hook_dest)],
            cwd=tmp, capture_output=True, text=True, timeout=30,
        )

        if expect_fail:
            return result.returncode != 0
        else:
            return result.returncode == 0


try:
    # Test 1: Clean file passes
    if run_hook_in_repo({"clean.py": "x = 1\ny = 2\n"}, expect_fail=False):
        tests_passed += 1

    # Test 2: .env file hard blocked (rule 2)
    if run_hook_in_repo({".env": "SECRET=abc123\n"}, expect_fail=True):
        tests_passed += 1

    # Test 3: .credentials file blocked (rule 2)
    if run_hook_in_repo({".credentials": "key=value\n"}, expect_fail=True):
        tests_passed += 1

    # Test 4: .key file blocked (rule 2)
    if run_hook_in_repo({"private.key": "-----BEGIN PRIVATE KEY-----\n"}, expect_fail=True):
        tests_passed += 1

    # Test 5: Multiple clean files pass
    if run_hook_in_repo({
        "a.py": "def foo():\n    return 1\n",
        "b.txt": "hello world\n",
    }, expect_fail=False):
        tests_passed += 1

except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.8 else 1)
