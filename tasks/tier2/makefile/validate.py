"""Validator for tier2-makefile task."""
import json
import subprocess
import sys
import re
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
makefile = workspace / "Makefile"

if not makefile.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

checks_passed = 0
total_checks = 8

content = makefile.read_text()

# Check 1: CC variable
if re.search(r'^CC\s*[?:]*=\s*gcc', content, re.MULTILINE):
    checks_passed += 1

# Check 2: CFLAGS with -Wall and -I include
if re.search(r'CFLAGS.*-Wall', content) and re.search(r'-I\s*include', content):
    checks_passed += 1

# Check 3: 'all' target exists
if re.search(r'^all\s*:', content, re.MULTILINE):
    checks_passed += 1

# Check 4: 'clean' target exists
if re.search(r'^clean\s*:', content, re.MULTILINE):
    checks_passed += 1

# Check 5: 'test' target exists
if re.search(r'^test\s*:', content, re.MULTILINE):
    checks_passed += 1

# Check 6: 'install' target exists
if re.search(r'^install\s*:', content, re.MULTILINE):
    checks_passed += 1

# Check 7: .PHONY declaration
if re.search(r'^\.PHONY\s*:', content, re.MULTILINE):
    checks_passed += 1

# Check 8: Uses automatic variables ($@, $<, or $^)
if re.search(r'\$[@<^]', content):
    checks_passed += 1

scores["correctness"] = checks_passed / total_checks

# Bonus: try make -n to see if it parses
try:
    result = subprocess.run(
        ["make", "-n"],
        capture_output=True, text=True, timeout=10,
        cwd=str(workspace),
    )
    if result.returncode == 0:
        # make -n succeeded, good sign
        pass
    else:
        # Makefile has syntax errors, reduce score
        scores["correctness"] *= 0.8
except Exception:
    pass

print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.8 else 1)
