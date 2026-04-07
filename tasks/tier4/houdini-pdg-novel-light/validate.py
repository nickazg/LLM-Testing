"""Validator for tier3-houdini-pdg task.

Source code analysis — reads the generated Python file and checks for
required patterns via string/regex matching.  Does NOT import hou.
"""
import json
import re
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "build_top_network.py"

# ---- Test 1: file exists ----
if not script.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0
src = script.read_text()
src_lower = src.lower()

tests_passed = 0
total_tests = 8

# Test 1: File exists (already confirmed above)
tests_passed += 1

# Test 2: Contains "import hou" or "hou."
if "import hou" in src or "hou." in src:
    tests_passed += 1

# Test 3: Contains topnet creation (createNode with "topnet" or "topnetwork")
if re.search(r'createNode\s*\(\s*["\']topnet', src_lower) or "topnet" in src_lower:
    tests_passed += 1

# Test 4: Contains Python Processor reference
if re.search(r'pythonprocessor|python_processor|python\s*processor', src_lower):
    tests_passed += 1

# Test 5: Contains partition reference
if re.search(r'partition|partitionbyattribute|partition\s*by', src_lower):
    tests_passed += 1

# Test 6: Contains waitforall
if "waitforall" in src_lower:
    tests_passed += 1

# Test 7: Contains work item attribute setting
if re.search(r'attrib|work_item|workitem|pdg', src_lower):
    tests_passed += 1

# Test 8: Contains node connection (.setInput or .setFirstInput or connect)
if re.search(r'\.setInput|\.setFirstInput|\.connect|setInput|setFirstInput', src):
    tests_passed += 1

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
