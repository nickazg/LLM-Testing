"""Validator for tier3-usd-render-settings task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "render_config.py"

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

    camera_usda = workspace / "camera_rig.usda"
    render_usda = workspace / "render_config.usda"

    # Test 1: Script runs without error (files created)
    if camera_usda.exists() and render_usda.exists():
        tests_passed += 1

    from pxr import Usd, UsdGeom, UsdRender, Sdf

    # --- Validate camera_rig.usda ---
    cam_stage = Usd.Stage.Open(str(camera_usda))

    # Test 2: camera_rig.usda exists with default prim /CameraRig
    dp = cam_stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/CameraRig"):
        tests_passed += 1

    # Test 3: /CameraRig/MainCamera is a UsdGeom.Camera
    cam = cam_stage.GetPrimAtPath("/CameraRig/MainCamera")
    if cam and cam.IsA(UsdGeom.Camera):
        tests_passed += 1

    # Test 4: Camera has focalLength attribute
    if cam and cam.IsValid():
        cam_api = UsdGeom.Camera(cam)
        fl = cam_api.GetFocalLengthAttr()
        if fl and fl.HasValue():
            tests_passed += 1

    # --- Validate render_config.usda ---
    render_stage = Usd.Stage.Open(str(render_usda))

    # Test 5: render_config.usda exists with default prim /Render
    dp = render_stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/Render"):
        tests_passed += 1

    # Test 6: RenderProduct exists
    product = render_stage.GetPrimAtPath("/Render/RenderProduct")
    if product and product.IsValid():
        tests_passed += 1

    # Test 7: At least 2 RenderVar prims exist under RenderProduct
    if product and product.IsValid():
        render_vars = [
            child for child in product.GetAllChildren()
            if child.IsA(UsdRender.Var)
        ]
        if len(render_vars) >= 2:
            tests_passed += 1

    # Test 8: RenderSettings exists with resolution attribute
    settings = render_stage.GetPrimAtPath("/Render/RenderSettings")
    if settings and settings.IsValid():
        settings_api = UsdRender.Settings(settings)
        res = settings_api.GetResolutionAttr()
        if res and res.HasValue():
            tests_passed += 1

except ImportError:
    # Fallback: text-based checks
    try:
        camera_usda = workspace / "camera_rig.usda"
        render_usda = workspace / "render_config.usda"

        if camera_usda.exists():
            content = camera_usda.read_text()
            checks = [
                "CameraRig" in content,
                "MainCamera" in content,
                "focalLength" in content,
            ]
            tests_passed += sum(checks)

        if render_usda.exists():
            content = render_usda.read_text()
            checks = [
                "Render" in content,
                "RenderProduct" in content,
                "RenderVar" in content or "renderVar" in content.lower(),
                "RenderSettings" in content,
                "resolution" in content.lower(),
            ]
            tests_passed += sum(checks)
    except Exception:
        pass
except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
