"""Validator for tier3-usd-shader-graph task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "shader_graph.py"

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

    mat_usda = workspace / "materials.usda"

    # Test 1: Script runs and materials.usda exists
    if mat_usda.exists():
        tests_passed += 1

    from pxr import Usd, UsdGeom, UsdShade, Sdf

    stage = Usd.Stage.Open(str(mat_usda))

    # Test 2: Default prim /Materials exists
    dp = stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/Materials"):
        tests_passed += 1

    # Test 3: /Materials/WoodMat exists and is a UsdShade.Material
    wood = stage.GetPrimAtPath("/Materials/WoodMat")
    if wood and wood.IsA(UsdShade.Material):
        tests_passed += 1

    # Test 4: WoodMat has a UsdPreviewSurface shader with roughness attribute
    wood_surface = stage.GetPrimAtPath("/Materials/WoodMat/Surface")
    if wood_surface and wood_surface.IsValid():
        shader = UsdShade.Shader(wood_surface)
        roughness = shader.GetInput("roughness")
        if roughness and roughness.Get() is not None:
            tests_passed += 1

    # Test 5: WoodMat has a texture shader (UsdUVTexture)
    wood_tex = stage.GetPrimAtPath("/Materials/WoodMat/WoodTex")
    if wood_tex and wood_tex.IsValid():
        shader = UsdShade.Shader(wood_tex)
        sid = shader.GetIdAttr()
        if sid and sid.HasValue():
            sid_val = sid.Get()
            if "UsdUVTexture" in str(sid_val):
                tests_passed += 1

    # Test 6: /Materials/MetalMat exists and is a UsdShade.Material
    metal = stage.GetPrimAtPath("/Materials/MetalMat")
    if metal and metal.IsA(UsdShade.Material):
        tests_passed += 1

    # Test 7: /Geometry/Table exists and is a Mesh
    table = stage.GetPrimAtPath("/Geometry/Table")
    if table and table.IsA(UsdGeom.Mesh):
        tests_passed += 1

    # Test 8: Table has a material binding or subset
    if table and table.IsValid():
        binding = UsdShade.MaterialBindingAPI(table)
        mat = binding.GetDirectBinding().GetMaterial()
        has_binding = mat.GetPrim().IsValid() if mat else False
        # Also check for subsets
        subsets = UsdGeom.Subset.GetAllGeomSubsets(UsdGeom.Imageable(table))
        if has_binding or len(subsets) > 0:
            tests_passed += 1

except ImportError:
    # Fallback: text-based checks
    try:
        mat_usda = workspace / "materials.usda"
        if mat_usda.exists():
            content = mat_usda.read_text()
            checks = [
                "Materials" in content,
                "WoodMat" in content,
                "UsdPreviewSurface" in content,
                "UsdUVTexture" in content,
                "MetalMat" in content,
                "Table" in content,
                "roughness" in content.lower(),
                "material:binding" in content or "materialBind" in content,
            ]
            tests_passed += sum(checks)
    except Exception:
        pass
except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
