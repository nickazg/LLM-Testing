"""Validator for tier2-log-processor task."""
import json
import subprocess
import sys
import os
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "analyze.sh"

if not script.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

# Make executable
os.chmod(script, 0o755)

try:
    result = subprocess.run(
        ["bash", str(script), "access.log"],
        capture_output=True, text=True, timeout=30,
        cwd=str(workspace),
    )
    output = result.stdout

    checks_passed = 0
    total_checks = 6

    # Check section headers exist
    if "Top 5 IPs" in output:
        checks_passed += 1
    if "Status Codes" in output:
        checks_passed += 1
    if "Top 3 Paths" in output:
        checks_passed += 1

    # Check top IP is 192.168.1.10 (25 requests)
    lines = output.splitlines()
    ip_section = False
    for line in lines:
        if "Top 5 IPs" in line:
            ip_section = True
            continue
        if ip_section and line.strip():
            if "192.168.1.10" in line:
                checks_passed += 1
            break

    # Check most common status is 200
    status_section = False
    for line in lines:
        if "Status Codes" in line:
            status_section = True
            continue
        if status_section and line.strip():
            if "200" in line:
                checks_passed += 1
            break

    # Check top path is /index.html
    path_section = False
    for line in lines:
        if "Top 3 Paths" in line:
            path_section = True
            continue
        if path_section and line.strip():
            if "/index.html" in line:
                checks_passed += 1
            break

    scores["correctness"] = checks_passed / total_checks
except Exception:
    pass

print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.8 else 1)
