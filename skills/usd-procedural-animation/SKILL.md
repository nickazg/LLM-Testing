# USD Skeletal Animation API Reference

## UsdSkel.Root — Skeleton Container

All skeletal data must live under a SkelRoot prim. This scopes skeleton evaluation.

```python
from pxr import Usd, UsdSkel, UsdGeom, Sdf, Gf, Vt

stage = Usd.Stage.CreateNew("skeleton_anim.usda")
root = UsdSkel.Root.Define(stage, "/Root")
stage.SetDefaultPrim(root.GetPrim())
```

## UsdSkel.Skeleton — Joint Topology

Defines the joint hierarchy using path tokens. Joints use `/` separator with NO leading `/`.

```python
skeleton = UsdSkel.Skeleton.Define(stage, "/Root/Skeleton")

# Joint paths define hierarchy — parent/child relationship via path
joints = ["Hips", "Hips/Spine", "Hips/Spine/Head", "Hips/LeftLeg", "Hips/RightLeg"]
skeleton.GetJointsAttr().Set(joints)
```

### Rest Transforms and Bind Transforms

Rest transforms define the default pose. Bind transforms define the world-space pose at bind time. Both are VtMatrix4dArray — one matrix per joint.

```python
from pxr import Gf, Vt

def make_translate_matrix(x, y, z):
    m = Gf.Matrix4d(1)  # identity
    m.SetTranslateOnly(Gf.Vec3d(x, y, z))
    return m

# One transform per joint, in the same order as joints list
rest_transforms = Vt.Matrix4dArray([
    make_translate_matrix(0, 0, 0),      # Hips (root)
    make_translate_matrix(0, 1, 0),       # Spine (relative to Hips)
    make_translate_matrix(0, 2, 0),       # Head (relative to Spine)
    make_translate_matrix(-0.5, -1, 0),   # LeftLeg (relative to Hips)
    make_translate_matrix(0.5, -1, 0),    # RightLeg (relative to Hips)
])

skeleton.GetRestTransformsAttr().Set(rest_transforms)
skeleton.GetBindTransformsAttr().Set(rest_transforms)
```

## UsdSkel.Animation — Time-Sampled Joint Motion

Animation holds per-frame joint transforms. Wire it to a skeleton via relationship.

```python
anim = UsdSkel.Animation.Define(stage, "/Root/Anim")

# Must match skeleton's joint list exactly
anim.GetJointsAttr().Set(joints)
```

### Authoring Time Samples

Translations, rotations, and scales are set per-frame. Each is an array with one entry per joint.

```python
# Animate Hips bouncing in Y over 24 frames
import math

for frame in range(1, 25):
    # All joints get a translation value per frame
    t = frame / 24.0
    hips_y = 0.5 * math.sin(t * math.pi * 2)  # bounce

    translations = Vt.Vec3fArray([
        Gf.Vec3f(0, hips_y, 0),        # Hips — animated
        Gf.Vec3f(0, 1, 0),             # Spine — static offset
        Gf.Vec3f(0, 2, 0),             # Head — static offset
        Gf.Vec3f(-0.5, -1, 0),         # LeftLeg — static
        Gf.Vec3f(0.5, -1, 0),          # RightLeg — static
    ])
    anim.GetTranslationsAttr().Set(translations, frame)

    # Rotations (quaternions) — identity for all joints
    rotations = Vt.QuatfArray([Gf.Quatf(1, 0, 0, 0)] * 5)
    anim.GetRotationsAttr().Set(rotations, frame)

    # Scales — uniform scale
    scales = Vt.Vec3hArray([Gf.Vec3h(1, 1, 1)] * 5)
    anim.GetScalesAttr().Set(scales, frame)
```

## UsdSkel.BindingAPI — Binding Mesh to Skeleton

Apply BindingAPI to a mesh to bind it to a skeleton and animation.

```python
# Create a simple mesh
mesh = UsdGeom.Mesh.Define(stage, "/Root/Mesh")
mesh.CreatePointsAttr([
    (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
    (-0.5, -0.5,  0.5), (0.5, -0.5,  0.5), (0.5, 0.5,  0.5), (-0.5, 0.5,  0.5),
])
mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
mesh.CreateFaceVertexIndicesAttr([
    0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5
])

# Apply binding API
binding = UsdSkel.BindingAPI.Apply(mesh.GetPrim())

# Point to skeleton
binding.CreateSkeletonRel().SetTargets(["/Root/Skeleton"])

# Point to animation source
binding.CreateAnimationSourceRel().SetTargets(["/Root/Anim"])

# Joint indices — which joint each vertex is bound to
# 8 vertices, 1 influence per vertex, all bound to joint 0 (Hips)
indices = Vt.IntArray([0] * 8)
binding.CreateJointIndicesPrimvar(False, 1).Set(indices)

# Joint weights — influence weight per vertex
weights = Vt.FloatArray([1.0] * 8)
binding.CreateJointWeightsPrimvar(False, 1).Set(weights)
```

### Joint Indices/Weights Detail
- `CreateJointIndicesPrimvar(constant, elementSize)` — constant=False means per-vertex, elementSize=number of influences per vertex
- `CreateJointWeightsPrimvar(constant, elementSize)` — same pattern
- Array length = num_vertices * elementSize
- Index values reference the joints list by position (0-based)

## Stage Save Pattern
```python
stage.GetRootLayer().Save()
```
