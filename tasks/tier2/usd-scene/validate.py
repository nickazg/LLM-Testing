"""Validator for tier2-usd-scene task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
build_py = workspace / "build_scene.py"

if not build_py.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

tests_passed = 0
total_tests = 8

try:
    # Run the build script
    result = subprocess.run(
        [sys.executable, str(build_py)],
        capture_output=True, text=True, timeout=30,
        cwd=str(workspace),
    )

    scene_usda = workspace / "scene.usda"
    if not scene_usda.exists():
        scores["correctness"] = 0.0
        print(json.dumps(scores))
        sys.exit(1)

    from pxr import Usd, UsdGeom, UsdShade, UsdLux, Sdf

    stage = Usd.Stage.Open(str(scene_usda))

    # Test 1: Default prim is /World
    default_prim = stage.GetDefaultPrim()
    if default_prim and default_prim.GetPath() == Sdf.Path("/World"):
        tests_passed += 1

    # Test 2: /World is an Xform
    world = stage.GetPrimAtPath("/World")
    if world and world.IsA(UsdGeom.Xform):
        tests_passed += 1

    # Test 3: /World/Ground is a Mesh with geometry
    ground = stage.GetPrimAtPath("/World/Ground")
    if ground and ground.IsA(UsdGeom.Mesh):
        mesh = UsdGeom.Mesh(ground)
        points = mesh.GetPointsAttr().Get()
        fvc = mesh.GetFaceVertexCountsAttr().Get()
        if points and len(points) >= 4 and fvc and len(fvc) >= 1:
            tests_passed += 1

    # Test 4: /World/Character exists with translate
    char = stage.GetPrimAtPath("/World/Character")
    if char and char.IsValid():
        xformable = UsdGeom.Xformable(char)
        xform_ops = xformable.GetOrderedXformOps()
        if xform_ops:
            tests_passed += 1

    # Test 5: /World/Character/Body is a Mesh
    body = stage.GetPrimAtPath("/World/Character/Body")
    if body and body.IsA(UsdGeom.Mesh):
        tests_passed += 1

    # Test 6: /World/Light is a DomeLight
    light = stage.GetPrimAtPath("/World/Light")
    if light and light.IsA(UsdLux.DomeLight):
        tests_passed += 1

    # Test 7: Material exists at /World/Looks/GroundMaterial
    mat_prim = stage.GetPrimAtPath("/World/Looks/GroundMaterial")
    if mat_prim and mat_prim.IsA(UsdShade.Material):
        tests_passed += 1

    # Test 8: Ground is bound to GroundMaterial
    if ground:
        binding_api = UsdShade.MaterialBindingAPI(ground)
        bound_mat, _ = binding_api.ComputeBoundMaterial()
        if bound_mat:
            mat_path = bound_mat.GetPrim().GetPath()
            if "GroundMaterial" in str(mat_path):
                tests_passed += 1

except ImportError:
    # pxr not installed — fall back to text parsing of .usda
    try:
        scene_usda = workspace / "scene.usda"
        if scene_usda.exists():
            content = scene_usda.read_text()
            # Basic text-based checks as fallback
            checks = [
                'def Xform "World"' in content,
                '"Ground"' in content and 'Mesh' in content,
                '"Character"' in content,
                '"Body"' in content,
                'DomeLight' in content or 'domeLight' in content.lower(),
                '"GroundMaterial"' in content,
                'Material' in content,
                'material:binding' in content or 'MaterialBindingAPI' in content,
            ]
            tests_passed = sum(checks)
    except Exception:
        pass
except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
