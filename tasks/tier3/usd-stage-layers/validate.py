"""Validator for tier3-usd-stage-layers task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "layer_opinions.py"

if not script.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

tests_passed = 0
total_tests = 8

try:
    # Run the script
    subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, timeout=30,
        cwd=str(workspace),
    )

    base_usda = workspace / "base_layer.usda"
    anim_usda = workspace / "anim_layer.usda"
    look_usda = workspace / "look_layer.usda"

    # Test 1: Script runs without error
    if base_usda.exists() and anim_usda.exists() and look_usda.exists():
        tests_passed += 1

    from pxr import Usd, UsdGeom, UsdShade, Sdf

    # Test 2: base_layer.usda exists with default prim /Scene
    base_stage = Usd.Stage.Open(str(base_usda))
    dp = base_stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/Scene"):
        tests_passed += 1

    # Test 3: /Scene/Character exists with translate
    char = base_stage.GetPrimAtPath("/Scene/Character")
    if char and char.IsValid():
        xf = UsdGeom.Xformable(char)
        ops = xf.GetOrderedXformOps()
        if ops:
            tests_passed += 1

    # Test 4: anim_layer.usda exists
    if anim_usda.exists():
        tests_passed += 1

    # Test 5: look_layer.usda exists
    if look_usda.exists():
        tests_passed += 1

    # Test 6: Opening composed stage resolves character prim
    # Build a composed stage with sublayers
    composed_stage = Usd.Stage.CreateInMemory()
    root_layer = composed_stage.GetRootLayer()
    root_layer.subLayerPaths.append(str(look_usda))
    root_layer.subLayerPaths.append(str(anim_usda))
    root_layer.subLayerPaths.append(str(base_usda))
    composed_char = composed_stage.GetPrimAtPath("/Scene/Character")
    if composed_char and composed_char.IsValid():
        tests_passed += 1

    # Test 7: Composed stage has time-sampled translate on Character
    if composed_char and composed_char.IsValid():
        xf = UsdGeom.Xformable(composed_char)
        ops = xf.GetOrderedXformOps()
        has_time_samples = False
        for op in ops:
            if op.GetNumTimeSamples() > 0:
                has_time_samples = True
                break
        if has_time_samples:
            tests_passed += 1

    # Test 8: A Material prim exists somewhere in the composed result
    found_material = False
    for prim in composed_stage.Traverse():
        if prim.IsA(UsdShade.Material):
            found_material = True
            break
    if found_material:
        tests_passed += 1

except ImportError:
    # Fallback: text-based checks
    try:
        for fname in ["base_layer.usda", "anim_layer.usda", "look_layer.usda"]:
            f = workspace / fname
            if f.exists():
                content = f.read_text()
                checks = [
                    "Scene" in content,
                    "Character" in content,
                ]
                tests_passed += sum(checks)
    except Exception:
        pass
except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
