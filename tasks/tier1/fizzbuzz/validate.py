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
