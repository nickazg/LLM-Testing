"""Validator for tier1-hello-world task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}

workspace = Path(".")

hello_py = workspace / "hello.py"
if not hello_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

try:
    result = subprocess.run(
        [sys.executable, str(hello_py)],
        capture_output=True, text=True, timeout=10,
    )
    if "Hello, World!" in result.stdout:
        scores["correctness"] = 1.0
    elif "hello" in result.stdout.lower() and "world" in result.stdout.lower():
        scores["correctness"] = 0.5
except Exception:
    pass

print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.5 else 1)
