"""Validator for tier3-usd-procedural-animation task."""
import json
import subprocess
import sys
from pathlib import Path

scores = {"correctness": 0.0, "completion": 0.0}
workspace = Path(".")
script = workspace / "animate_skeleton.py"

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

    skel_usda = workspace / "skeleton_anim.usda"

    # Test 1: Script runs without error and file exists
    if skel_usda.exists():
        tests_passed += 1

    from pxr import Usd, UsdGeom, UsdSkel, Sdf

    stage = Usd.Stage.Open(str(skel_usda))

    # Test 2: Default prim /Root is a UsdSkel.Root
    dp = stage.GetDefaultPrim()
    if dp and dp.GetPath() == Sdf.Path("/Root") and dp.IsA(UsdSkel.Root):
        tests_passed += 1

    # Test 3: /Root/Skeleton exists and is a UsdSkel.Skeleton
    skel = stage.GetPrimAtPath("/Root/Skeleton")
    if skel and skel.IsA(UsdSkel.Skeleton):
        tests_passed += 1

    # Test 4: Skeleton has joints attribute with 5 joints
    if skel and skel.IsValid():
        skel_api = UsdSkel.Skeleton(skel)
        joints = skel_api.GetJointsAttr()
        if joints and joints.HasValue():
            joint_list = joints.Get()
            if joint_list and len(joint_list) == 5:
                tests_passed += 1

    # Test 5: /Root/Anim exists and is a UsdSkel.Animation
    anim = stage.GetPrimAtPath("/Root/Anim")
    if anim and anim.IsA(UsdSkel.Animation):
        tests_passed += 1

    # Test 6: Animation has time samples
    if anim and anim.IsValid():
        anim_api = UsdSkel.Animation(anim)
        trans = anim_api.GetTranslationsAttr()
        if trans and trans.GetNumTimeSamples() > 0:
            tests_passed += 1

    # Test 7: /Root/Mesh exists and is a UsdGeom.Mesh
    mesh = stage.GetPrimAtPath("/Root/Mesh")
    if mesh and mesh.IsA(UsdGeom.Mesh):
        tests_passed += 1

    # Test 8: Mesh has skel binding attributes (jointIndices or jointWeights)
    if mesh and mesh.IsValid():
        ji = mesh.GetAttribute("primvars:skel:jointIndices")
        jw = mesh.GetAttribute("primvars:skel:jointWeights")
        if (ji and ji.HasValue()) or (jw and jw.HasValue()):
            tests_passed += 1

except ImportError:
    # Fallback: text-based checks
    try:
        skel_usda = workspace / "skeleton_anim.usda"
        if skel_usda.exists():
            content = skel_usda.read_text()
            checks = [
                "SkelRoot" in content,
                "Skeleton" in content,
                "Hips" in content,
                "Animation" in content or "SkelAnimation" in content,
                "Mesh" in content,
                "jointIndices" in content or "jointWeights" in content,
            ]
            tests_passed += sum(checks)
    except Exception:
        pass
except Exception:
    pass

scores["correctness"] = tests_passed / total_tests
print(json.dumps(scores))
sys.exit(0 if scores["correctness"] >= 0.7 else 1)
