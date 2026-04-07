# PointInstancer & Collections Quick Reference

## Stage Access (REQUIRED)

```python
import hou
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

> **WARNING:** Never use `Usd.Stage.CreateNew()` — it creates a disconnected stage. Always use `hou.pwd().editableStage()`.

## PointInstancer Workflow

**Step 1: Create Instancer**
```python
instancer = UsdGeom.PointInstancer.Define(stage, "/Scene/Instances")
```

**Step 2: Link Prototypes**
```python
instancer.GetPrototypesRel().SetTargets([
    Sdf.Path("/Scene/Prototypes/A"),
    Sdf.Path("/Scene/Prototypes/B"),
])
```

**Step 3: Set Indices (0-indexed mapping to prototypes)**
```python
instancer.GetProtoIndicesAttr().Set(Vt.IntArray([0, 1, 0, 1]))
```

**Step 4: Set Positions**
```python
instancer.GetPositionsAttr().Set(Vt.Vec3fArray([
    Gf.Vec3f(0, 0, 0), Gf.Vec3f(2, 0, 0),
    Gf.Vec3f(4, 0, 0), Gf.Vec3f(6, 0, 0),
]))
```

**Step 5: Set Orientations (quaternions, identity = no rotation)**
```python
instancer.GetOrientationsAttr().Set(
    Vt.QuathArray([Gf.Quath(1, 0, 0, 0)] * 4)
)
```

## Prototype Definition

Prototypes are Xform + Mesh prims:

```python
proto = UsdGeom.Xform.Define(stage, "/Scene/Prototypes/A")
mesh = UsdGeom.Mesh.Define(stage, "/Scene/Prototypes/A/Shape")
mesh.GetPointsAttr().Set(Vt.Vec3fArray([
    (-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5), (-0.5, 0, 0.5),
    (-0.5, 1, -0.5), (0.5, 1, -0.5), (0.5, 1, 0.5), (-0.5, 1, 0.5),
]))
mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray([4, 4, 4, 4, 4, 4]))
mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray([
    0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5
]))
```

## Collection API

```python
collection = Usd.CollectionAPI.Apply(scene_prim, "mycollection")
collection.GetIncludesRel().AddTarget("/Scene/Instances")
collection.GetIncludesRel().AddTarget("/Scene/Prototypes/A")
```

## Default Prim

```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())
```
