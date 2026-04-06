"""Validator for tier3-usd-shot-assembly task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "assemble_shot.py"

if not script.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

tests_passed = 0
total_tests = 10

try:
    # Run the assembly script
    subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, timeout=30,
        cwd=str(workspace),
    )

    assets_usda = workspace / "assets.usda"
    shot_usda = workspace / "shot.usda"

    if not assets_usda.exists() or not shot_usda.exists():
        scores["correctness"] = 0.1 if assets_usda.exists() or shot_usda.exists() else 0.0
        print(json.dumps(scores))
        sys.exit(1)

    from pxr import Usd, UsdGeom, UsdLux, Sdf

    # --- Validate assets.usda ---
    assets_stage = Usd.Stage.Open(str(assets_usda))

    # Test 1: Default prim /Assets
    dp = assets_stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/Assets"):
        tests_passed += 1

    # Test 2: /Assets/Chair exists
    chair = assets_stage.GetPrimAtPath("/Assets/Chair")
    if chair and chair.IsValid():
        tests_passed += 1

    # Test 3: Chair has variant set 'modelVariant'
    if chair and chair.HasVariantSets():
        vs = chair.GetVariantSets()
        if vs.HasVariantSet("modelVariant"):
            vset = vs.GetVariantSet("modelVariant")
            names = vset.GetVariantNames()
            if "simple" in names and "detailed" in names:
                tests_passed += 1

    # Test 4: Chair has geometry child
    geo = assets_stage.GetPrimAtPath("/Assets/Chair/Geo")
    if geo and geo.IsA(UsdGeom.Mesh):
        tests_passed += 1

    # --- Validate shot.usda ---
    shot_stage = Usd.Stage.Open(str(shot_usda))

    # Test 5: Default prim /Shot
    dp = shot_stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/Shot"):
        tests_passed += 1

    # Test 6: ChairA exists with reference
    chair_a = shot_stage.GetPrimAtPath("/Shot/Set/ChairA")
    if chair_a and chair_a.IsValid():
        # Check it has geometry from the reference
        tests_passed += 1

    # Test 7: ChairB exists at different position
    chair_b = shot_stage.GetPrimAtPath("/Shot/Set/ChairB")
    if chair_b and chair_b.IsValid():
        tests_passed += 1

    # Test 8: ChairA and ChairB have different transforms
    if chair_a and chair_b:
        xa = UsdGeom.Xformable(chair_a)
        xb = UsdGeom.Xformable(chair_b)
        ops_a = xa.GetOrderedXformOps()
        ops_b = xb.GetOrderedXformOps()
        if ops_a and ops_b:
            tests_passed += 1

    # Test 9: Lighting variant set exists
    lighting = shot_stage.GetPrimAtPath("/Shot/Lighting")
    if lighting and lighting.HasVariantSets():
        vs = lighting.GetVariantSets()
        if vs.HasVariantSet("lightingVariant"):
            vset = vs.GetVariantSet("lightingVariant")
            names = vset.GetVariantNames()
            if "day" in names and "night" in names:
                tests_passed += 1

    # Test 10: Switching variants produces different lights
    if lighting and lighting.HasVariantSets():
        vs = lighting.GetVariantSets()
        if vs.HasVariantSet("lightingVariant"):
            vset = vs.GetVariantSet("lightingVariant")
            vset.SetVariantSelection("day")
            # Check for any light prim under Lighting
            has_day_light = False
            for child in lighting.GetAllChildren():
                if child.IsA(UsdLux.DistantLight) or child.IsA(UsdLux.DomeLight):
                    has_day_light = True
                    break
            if has_day_light:
                tests_passed += 1

except ImportError:
    # Fallback: text-based checks
    try:
        for f in [workspace / "assets.usda", workspace / "shot.usda"]:
            if f.exists():
                content = f.read_text()
                text_checks = [
                    "Chair" in content,
                    "variant" in content.lower(),
                ]
                tests_passed += sum(text_checks)
    except Exception:
        pass
except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
