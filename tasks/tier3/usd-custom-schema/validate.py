"""Validator for tier3-usd-custom-schema task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "custom_metadata.py"

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

    pipeline_usda = workspace / "pipeline.usda"

    # Test 1: Script runs and pipeline.usda exists
    if pipeline_usda.exists():
        tests_passed += 1

    from pxr import Usd, UsdGeom, Sdf, Kind

    stage = Usd.Stage.Open(str(pipeline_usda))

    # Test 2: Default prim /Project exists
    dp = stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/Project"):
        tests_passed += 1

    # Test 3: /Project has customData with "pipeline:version"
    if dp and dp.IsValid():
        custom_data = dp.GetCustomData()
        if custom_data and "pipeline:version" in custom_data:
            tests_passed += 1

    # Test 4: /Project has assetInfo with name
    if dp and dp.IsValid():
        asset_info = dp.GetAssetInfo()
        if asset_info and "name" in asset_info:
            tests_passed += 1

    # Test 5: /Project/Hero exists with purpose "render"
    hero = stage.GetPrimAtPath("/Project/Hero")
    if hero and hero.IsValid():
        img = UsdGeom.Imageable(hero)
        purpose = img.GetPurposeAttr()
        if purpose and purpose.Get() == UsdGeom.Tokens.render:
            tests_passed += 1

    # Test 6: /Project/Hero/Proxy exists with purpose "proxy"
    proxy = stage.GetPrimAtPath("/Project/Hero/Proxy")
    if proxy and proxy.IsValid():
        img = UsdGeom.Imageable(proxy)
        purpose = img.GetPurposeAttr()
        if purpose and purpose.Get() == UsdGeom.Tokens.proxy:
            tests_passed += 1

    # Test 7: /Project/Hero has a custom property containing "shotName" or "SH010"
    if hero and hero.IsValid():
        shot_attr = hero.GetAttribute("custom:shotName")
        if shot_attr and shot_attr.HasValue():
            val = shot_attr.Get()
            if val == "SH010" or "SH010" in str(val):
                tests_passed += 1

    # Test 8: /Project/Hero has kind set to "component"
    if hero and hero.IsValid():
        model = Usd.ModelAPI(hero)
        kind = model.GetKind()
        if kind == Kind.Tokens.component:
            tests_passed += 1

except ImportError:
    # Fallback: text-based checks
    try:
        pipeline_usda = workspace / "pipeline.usda"
        if pipeline_usda.exists():
            content = pipeline_usda.read_text()
            checks = [
                "Project" in content,
                "pipeline:version" in content or "pipeline" in content,
                "assetInfo" in content,
                "Hero" in content,
                "proxy" in content.lower(),
                "SH010" in content,
                "component" in content,
                "render" in content,
            ]
            tests_passed += sum(checks)
    except Exception:
        pass
except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
