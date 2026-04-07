"""Validator for tier3-houdini-solaris-instancing task.

Source code analysis — reads the generated Python file and checks for
required patterns via string/regex matching.  Does NOT import hou.
"""
import json
import re
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "solaris_instancing.py"

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

# Test 2: Contains hou.pwd().editableStage()
if "hou.pwd().editableStage()" in src or re.search(r'hou\s*\.\s*pwd\s*\(\s*\)\s*\.\s*editableStage', src):
    tests_passed += 1

# Test 3: Contains UsdGeom.PointInstancer
if "UsdGeom.PointInstancer" in src or "PointInstancer" in src:
    tests_passed += 1

# Test 4: Contains "protoIndices" or "GetProtoIndicesAttr"
if "protoIndices" in src or "GetProtoIndicesAttr" in src or "ProtoIndices" in src:
    tests_passed += 1

# Test 5: Contains "positions" or "GetPositionsAttr"
if re.search(r'GetPositionsAttr|\.positions|SetPositions|positions', src_lower):
    tests_passed += 1

# Test 6: Contains prototype references (at least 3 tree prims or "Prototypes")
tree_refs = re.findall(r'Tree[ABC]|Prototypes', src)
if len(tree_refs) >= 3:
    tests_passed += 1

# Test 7: Contains "orientations" or "GetOrientationsAttr"
if re.search(r'orientations|GetOrientationsAttr', src_lower):
    tests_passed += 1

# Test 8: Contains "Collection" or "CollectionAPI"
if "Collection" in src or "CollectionAPI" in src:
    tests_passed += 1

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
