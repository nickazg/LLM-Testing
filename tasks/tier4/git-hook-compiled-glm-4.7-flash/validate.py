"""Validator for tier3-git-hook task."""
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
total_tests = 6


def run_hook_in_repo(staged_files: dict[str, str | bytes], expect_fail: bool) -> bool:
    """Create a temp git repo, stage files, run the hook, check result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Init git repo
        subprocess.run(["git", "init"], cwd=tmp, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp, capture_output=True)
        # Initial commit so we can stage
        (tmp / "README.md").write_text("init")
        subprocess.run(["git", "add", "README.md"], cwd=tmp, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp, capture_output=True)

        # Create and stage test files
        for name, content in staged_files.items():
            fpath = tmp / name
            fpath.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                fpath.write_bytes(content)
            else:
                fpath.write_text(content)
            subprocess.run(["git", "add", name], cwd=tmp, capture_output=True)

        # Copy hook
        hook_dest = tmp / ".git" / "hooks" / "pre-commit"
        hook_dest.write_text(hook.read_text())
        os.chmod(hook_dest, 0o755)

        # Run hook
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

    # Test 2: Large file rejected (>5MB)
    big_content = b"x" * (5 * 1024 * 1024 + 1)
    if run_hook_in_repo({"big.bin": big_content}, expect_fail=True):
        tests_passed += 1

    # Test 3: Debug print() rejected
    if run_hook_in_repo({"debug.py": "x = 1\nprint(x)\n"}, expect_fail=True):
        tests_passed += 1

    # Test 4: Trailing whitespace rejected
    if run_hook_in_repo({"spaces.txt": "hello   \nworld\n"}, expect_fail=True):
        tests_passed += 1

    # Test 5: Syntax error in Python rejected
    if run_hook_in_repo({"broken.py": "def foo(\n"}, expect_fail=True):
        tests_passed += 1

    # Test 6: Multiple clean files pass
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
