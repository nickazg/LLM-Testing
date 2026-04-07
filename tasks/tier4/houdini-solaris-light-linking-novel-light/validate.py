"""Validator for tier3-houdini-solaris-light-linking task.

Source code analysis — reads the generated Python file and checks for
required patterns via string/regex matching.  Does NOT import hou.
"""
import json
import re
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "solaris_light_linking.py"

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

# Test 3: Contains at least 3 different light types/instances (DistantLight and DomeLight)
distant_count = len(re.findall(r'DistantLight', src))
dome_count = len(re.findall(r'DomeLight', src))
if distant_count >= 2 and dome_count >= 1:
    tests_passed += 1

# Test 4: Contains "purpose" attribute setting
if re.search(r'purpose|Purpose', src):
    tests_passed += 1

# Test 5: Contains "LightFilter" or "BarnDoor" or "barndoor" or light filter child prim
if re.search(r'LightFilter|BarnDoor|barndoor|barn_door', src):
    tests_passed += 1

# Test 6: Contains "CollectionAPI" or "collection" for light linking
if "CollectionAPI" in src or "collection" in src_lower:
    tests_passed += 1

# Test 7: Contains at least 2 collection definitions (for KeyLight and RimLight linking)
collection_defs = re.findall(r'CollectionAPI|collection.*lightLink|lightLink', src)
if len(collection_defs) >= 2:
    tests_passed += 1

# Test 8: Contains intensity setting with values > 1000 (production-scale values)
intensity_values = re.findall(r'intensity.*?(\d+)', src_lower)
high_intensity = [v for v in intensity_values if int(v) > 1000]
if len(high_intensity) >= 1:
    tests_passed += 1

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
