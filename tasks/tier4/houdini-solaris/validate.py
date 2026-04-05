"""Validator for tier3-houdini-solaris task."""
import json
import sys
import os
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "solaris_lop.py"

if not script.exists():
    print(json.dumps(scores))
    sys.exit(1)

scores["completion"] = 1.0

tests_passed = 0
total_tests = 10

try:
    # Add workspace to path so `import hou` finds the mock
    sys.path.insert(0, str(workspace))

    # Execute the script in-process so it populates the mock's USD stage
    exec(compile(script.read_text(), str(script), "exec"), {"__name__": "__main__"})

    # Get the stage from the mock
    import hou
    stage = hou._get_stage()

    from pxr import Usd, UsdGeom, UsdShade, UsdLux, Sdf, Kind

    # Test 1: Default prim is /Scene
    dp = stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/Scene"):
        tests_passed += 1

    # Test 2: /Scene/Ground is a Mesh with geometry
    ground = stage.GetPrimAtPath("/Scene/Ground")
    if ground and ground.IsA(UsdGeom.Mesh):
        mesh = UsdGeom.Mesh(ground)
        points = mesh.GetPointsAttr().Get()
        if points and len(points) >= 4:
            tests_passed += 1

    # Test 3: /Scene/Hero exists as Xform with translate
    hero = stage.GetPrimAtPath("/Scene/Hero")
    if hero and hero.IsValid():
        xf = UsdGeom.Xformable(hero)
        ops = xf.GetOrderedXformOps()
        if ops:
            tests_passed += 1

    # Test 4: /Scene/Hero/Body is a Mesh
    body = stage.GetPrimAtPath("/Scene/Hero/Body")
    if body and body.IsA(UsdGeom.Mesh):
        mesh = UsdGeom.Mesh(body)
        points = mesh.GetPointsAttr().Get()
        if points and len(points) >= 8:
            tests_passed += 1

    # Test 5: KeyLight is a DistantLight
    key = stage.GetPrimAtPath("/Scene/Lighting/KeyLight")
    if key and key.IsA(UsdLux.DistantLight):
        tests_passed += 1

    # Test 6: FillLight is a DomeLight
    fill = stage.GetPrimAtPath("/Scene/Lighting/FillLight")
    if fill and fill.IsA(UsdLux.DomeLight):
        tests_passed += 1

    # Test 7: Material exists
    mat_prim = stage.GetPrimAtPath("/Scene/Materials/HeroMat")
    if mat_prim and mat_prim.IsA(UsdShade.Material):
        tests_passed += 1

    # Test 8: Material has a shader with diffuseColor
    # Look for a UsdPreviewSurface shader child
    if mat_prim:
        for child in mat_prim.GetAllChildren():
            if child.IsA(UsdShade.Shader):
                shader = UsdShade.Shader(child)
                id_attr = shader.GetIdAttr()
                if id_attr and id_attr.Get() == "UsdPreviewSurface":
                    tests_passed += 1
                    break

    # Test 9: Hero/Body bound to HeroMat
    if body:
        binding_api = UsdShade.MaterialBindingAPI(body)
        bound_mat, _ = binding_api.ComputeBoundMaterial()
        if bound_mat and "HeroMat" in str(bound_mat.GetPrim().GetPath()):
            tests_passed += 1

    # Test 10: Hero has Kind = component
    if hero:
        model = Usd.ModelAPI(hero)
        kind = model.GetKind()
        if kind == Kind.Tokens.component:
            tests_passed += 1

except ImportError as e:
    # pxr not available — can't validate Solaris tasks without USD
    # Give minimal credit for file existence
    pass
except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
