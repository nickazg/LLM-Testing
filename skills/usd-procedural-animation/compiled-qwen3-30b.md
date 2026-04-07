# Connect animation to skeleton

## Imports

```python
from pxr import Usd, UsdSkel, UsdGeom, Sdf, Gf, Vt
import math
```

## SkelRoot (Required Container)

All skeletal data must be under a SkelRoot.
```python
stage = Usd.Stage.CreateNew("output.usda")
root = UsdSkel.Root.Define(stage, "/Root")
stage.SetDefaultPrim(root.GetPrim())
```

## Skeleton — Joint Hierarchy

```python
skeleton = UsdSkel.Skeleton.Define(stage, "/Root/Skeleton")

joints = ["Hips", "Hips/Spine", "Hips/Spine/Head"]
skeleton.GetJointsAttr().Set(joints)

rest_xforms = Vt.Matrix4dArray()
for i in range(len(joints)):
    m = Gf.Matrix4d(1)
    m.SetTranslateOnly(Gf.Vec3d(0, i, 0))
    rest_xforms.append(m)

skeleton.GetRestTransformsAttr().Set(rest_xforms)
skeleton.GetBindTransformsAttr().Set(rest_xforms)
```

## Animation — Time-Sampled Joint Motion

```python
anim = UsdSkel.Animation.Define(stage, "/Root/Anim")
anim.GetJointsAttr().Set(joints)  # Must match skeleton's joints

for frame in range(1, 25):
    translations = Vt.Vec3fArray()
    rotations = Vt.QuatfArray()
    scales = Vt.Vec3hArray()
    
    for i, joint in enumerate(joints):
        translations.append(Gf.Vec3f(0, 0, 0))
        rotations.append(Gf.Quatf(1, 0, 0, 0))  # Identity: (w, x, y, z)
        scales.append(Gf.Vec3h(1, 1, 1))
    
    anim.GetTranslationsAttr().Set(translations, frame)
    anim.GetRotationsAttr().Set(rotations, frame)
    anim.GetScalesAttr().Set(scales, frame)

skeleton.GetAnimationSourceRel().SetTargets(["/Root/Anim"])
```

## Save

```python
stage.GetRootLayer().Save()
```

## Key Rules

1. Joint paths have NO leading "/" (e.g., `"Hips/Spine"`, not `"/Hips/Spine"`)
2. Animation joints list must match skeleton joints list exactly
3. All transform arrays (rest, bind, anim) must have same length as joints list
4. Quaternions use (w, x, y, z) order
5. Everything must be under a SkelRoot
