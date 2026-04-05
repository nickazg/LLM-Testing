"""Validator for tier2-cli-tool task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
wordcount_py = workspace / "wordcount.py"

if not wordcount_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

# Expected values (deterministic, computed from template files)
# sample1.txt: 6 lines, 51 words, 329 chars
# sample2.txt: 4 lines, 18 words, 103 chars
EXPECTED = {
    "sample1.txt": {"lines": 6, "words": 51, "chars": 329},
    "sample2.txt": {"lines": 4, "words": 18, "chars": 103},
}

passed = 0
total = 4


def run_wc(*args):
    """Run wordcount.py with given arguments and return stdout."""
    cmd = [sys.executable, str(wordcount_py)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return result.stdout.strip(), result.returncode


def extract_number(output, filename=None):
    """Extract the first number from output, optionally for a specific file line."""
    for line in output.splitlines():
        if filename and filename not in line:
            continue
        parts = line.split()
        for part in parts:
            try:
                return int(part)
            except ValueError:
                continue
    return None


def extract_numbers(output, filename=None):
    """Extract all numbers from a line of output, optionally for a specific file line."""
    nums = []
    for line in output.splitlines():
        if filename and filename not in line:
            continue
        parts = line.split()
        for part in parts:
            try:
                nums.append(int(part))
            except ValueError:
                continue
        if nums:
            return nums
    return nums


try:
    # Test 1: --lines with single file
    out, rc = run_wc("--lines", "sample1.txt")
    if rc == 0:
        num = extract_number(out, "sample1.txt")
        if num is None:
            num = extract_number(out)
        if num == EXPECTED["sample1.txt"]["lines"]:
            passed += 1

    # Test 2: --words with two files
    out, rc = run_wc("--words", "sample1.txt", "sample2.txt")
    if rc == 0:
        n1 = extract_number(out, "sample1.txt")
        n2 = extract_number(out, "sample2.txt")
        if n1 == EXPECTED["sample1.txt"]["words"] and n2 == EXPECTED["sample2.txt"]["words"]:
            passed += 1

    # Test 3: --chars with single file
    out, rc = run_wc("--chars", "sample1.txt")
    if rc == 0:
        num = extract_number(out, "sample1.txt")
        if num is None:
            num = extract_number(out)
        if num == EXPECTED["sample1.txt"]["chars"]:
            passed += 1

    # Test 4: no flags (default = all three) with single file
    out, rc = run_wc("sample1.txt")
    if rc == 0:
        nums = extract_numbers(out, "sample1.txt")
        if not nums:
            nums = extract_numbers(out)
        exp = EXPECTED["sample1.txt"]
        # Check that lines, words, and chars all appear in the output
        if (exp["lines"] in nums and exp["words"] in nums and exp["chars"] in nums):
            passed += 1

except Exception:
    pass

scores["correctness"] = passed / total

print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.5 else 1)
