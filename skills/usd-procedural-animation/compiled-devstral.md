# Format: CreateJointIndicesPrimvar(constant, elementSize)

## Complete Setup

```python
from pxr import Usd, UsdSkel, UsdGeom, Gf, Vt
import math

stage = Usd.Stage.CreateNew("anim.usda")
root = UsdSkel.Root.Define(stage, "/Root")
stage.SetDefaultPrim(root.GetPrim())
```

## Skeleton with Joints

```python
skeleton = UsdSkel.Skeleton.Define(stage, "/Root/Skeleton")

joints = ["Hips", "Hips/Spine", "Hips/Spine/Head", "Hips/LeftLeg"]
skeleton.GetJointsAttr().Set(joints)

def make_matrix(x, y, z):
    m = Gf.Matrix4d(1)
    m.SetTranslateOnly(Gf.Vec3d(x, y, z))
    return m

rest = Vt.Matrix4dArray([make_matrix(0,0,0), make_matrix(0,1,0), make_matrix(0,2,0), make_matrix(-0.5,-1,0)])
skeleton.GetRestTransformsAttr().Set(rest)
skeleton.GetBindTransformsAttr().Set(rest)
```

## Animation with Time Samples

```python
anim = UsdSkel.Animation.Define(stage, "/Root/Anim")
anim.GetJointsAttr().Set(joints)  # Must match skeleton joints

for frame in range(1, 25):
    y_offset = 0.5 * math.sin(frame / 24.0 * math.pi * 2)
    
    translations = Vt.Vec3fArray([
        Gf.Vec3f(0, y_offset, 0),  # Animated Hips
        Gf.Vec3f(0, 1, 0),
        Gf.Vec3f(0, 2, 0),
        Gf.Vec3f(-0.5, -1, 0),
    ])
    anim.GetTranslationsAttr().Set(translations, frame)
    
    # Identity quaternions (w, x, y, z)
    anim.GetRotationsAttr().Set(Vt.QuatfArray([Gf.Quatf(1,0,0,0)] * 4), frame)
    anim.GetScalesAttr().Set(Vt.Vec3hArray([Gf.Vec3h(1,1,1)] * 4), frame)
```

## Bind Mesh to Skeleton

```python
mesh = UsdGeom.Mesh.Define(stage, "/Root/Mesh")

binding = UsdSkel.BindingAPI.Apply(mesh.GetPrim())
binding.CreateSkeletonRel().SetTargets(["/Root/Skeleton"])
binding.CreateAnimationSourceRel().SetTargets(["/Root/Anim"])

binding.CreateJointIndicesPrimvar(False, 1).Set(Vt.IntArray([0] * num_vertices))
binding.CreateJointWeightsPrimvar(False, 1).Set(Vt.FloatArray([1.0] * num_vertices))
```

## Save

```python
stage.GetRootLayer().Save()
```
