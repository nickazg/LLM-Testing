"""Validator for tier2-csv-pipeline task."""
import csv
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")

pipeline_py = workspace / "pipeline.py"
if not pipeline_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 0.5  # Script exists

# Run the pipeline
try:
    result = subprocess.run(
        [sys.executable, str(pipeline_py)],
        capture_output=True, text=True, timeout=15,
        cwd=str(workspace),
    )
except Exception:
    print(json.dumps(scores))
    sys.exit(1)

output_csv = workspace / "output.csv"
if not output_csv.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0  # Both files exist

# Expected results (pre-computed from input.csv active rows)
expected = {
    "Engineering": {"avg_salary": 96200.00, "count": 5},
    "HR": {"avg_salary": 81250.00, "count": 4},
    "Marketing": {"avg_salary": 76500.00, "count": 4},
    "Sales": {"avg_salary": 70666.67, "count": 3},
}

try:
    with open(output_csv) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print(json.dumps(scores))
        sys.exit(1)

    correct_rows = 0
    total_expected = len(expected)

    for row in rows:
        dept = row.get("department", "").strip()
        if dept not in expected:
            continue
        try:
            avg = float(row.get("avg_salary", 0))
            count = int(row.get("count", 0))
        except (ValueError, TypeError):
            continue

        exp = expected[dept]
        avg_ok = abs(avg - exp["avg_salary"]) < 0.1
        count_ok = count == exp["count"]
        if avg_ok and count_ok:
            correct_rows += 1

    # Check sort order
    depts_in_output = [r.get("department", "").strip() for r in rows]
    sorted_ok = depts_in_output == sorted(depts_in_output)

    row_score = correct_rows / total_expected if total_expected else 0
    scores["correctness"] = row_score * 0.8 + (0.2 if sorted_ok else 0.0)

except Exception:
    pass

print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.5 else 1)
