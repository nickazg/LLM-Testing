"""Validator for tier3-houdini-solaris-render task.

Source code analysis — reads the generated Python file and checks for
required patterns via string/regex matching.  Does NOT import hou.
"""
import json
import re
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "solaris_render_setup.py"

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

# Test 3: Contains UsdRender.Settings or RenderSettings
if "UsdRender.Settings" in src or "RenderSettings" in src:
    tests_passed += 1

# Test 4: Contains UsdRender.Product or RenderProduct
if "UsdRender.Product" in src or "RenderProduct" in src:
    tests_passed += 1

# Test 5: Contains UsdRender.Var or RenderVar
if "UsdRender.Var" in src or "RenderVar" in src:
    tests_passed += 1

# Test 6: Contains UsdGeom.Camera
if "UsdGeom.Camera" in src or "Camera" in src:
    tests_passed += 1

# Test 7: Contains resolution or pixelAspectRatio reference
if re.search(r'resolution|pixelAspectRatio|pixelaspectratio', src_lower):
    tests_passed += 1

# Test 8: Contains karma or sample or "sampleCount" reference
if re.search(r'karma|samplecount|sampleCount|sample_count', src_lower):
    tests_passed += 1

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
