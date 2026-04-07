# Scales

## Imports and Stage Setup

```python
from pxr import Usd, UsdSkel, Gf, Vt

stage = Usd.Stage.CreateNew("skeleton.usda")
root = UsdSkel.Root.Define(stage, "/Root")
```

## Create Skeleton with Joints

```python
skeleton = UsdSkel.Skeleton.Define(stage, "/Root/Skeleton")

joints = ["Hips", "Hips/Spine", "Hips/Spine/Head"]
skeleton.GetJointsAttr().Set(joints)
```

## Set Rest/Bind Transforms

One matrix per joint. Use identity for simple cases:
```python
transforms = Vt.Matrix4dArray([Gf.Matrix4d(1.0)] * len(joints))
skeleton.GetRestTransformsAttr().Set(transforms)
skeleton.GetBindTransformsAttr().Set(transforms)
```

## Create Animation

```python
anim = UsdSkel.Animation.Define(stage, "/Root/Anim")
anim.GetJointsAttr().Set(joints)  # must match skeleton joints
```

## Set Frame Data

Per-joint arrays: translations (Vec3f), rotations (Quatf), scales (Vec3h):
```python
trans = Vt.Vec3fArray([
    Gf.Vec3f(0, 0.5, 0),   # Hips
    Gf.Vec3f(0, 1.0, 0),   # Spine
    Gf.Vec3f(0, 0.5, 0),   # Head
])
anim.GetTranslationsAttr().Set(trans, 1)

rots = Vt.QuatfArray([Gf.Quatf(1, 0, 0, 0)] * len(joints))
anim.GetRotationsAttr().Set(rots, 1)

scales = Vt.Vec3hArray([Gf.Vec3h(1, 1, 1)] * len(joints))
anim.GetScalesAttr().Set(scales, 1)
```

## Save

```python
stage.GetRootLayer().Save()
```
