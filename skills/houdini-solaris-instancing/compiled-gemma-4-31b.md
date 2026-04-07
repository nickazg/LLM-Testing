# Set orientations (quaternion per instance, identity = no rotation)

## Setup

```python
import hou
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

## PointInstancer

```python
instancer = UsdGeom.PointInstancer.Define(stage, "/Scene/Instances")

instancer.GetPrototypesRel().SetTargets([
    Sdf.Path("/Scene/Prototypes/A"),
    Sdf.Path("/Scene/Prototypes/B"),
])

instancer.GetProtoIndicesAttr().Set(Vt.IntArray([0, 1, 0, 1]))

instancer.GetPositionsAttr().Set(Vt.Vec3fArray([
    Gf.Vec3f(0, 0, 0), Gf.Vec3f(2, 0, 0), Gf.Vec3f(4, 0, 0), Gf.Vec3f(6, 0, 0)
]))

instancer.GetOrientationsAttr().Set(Vt.QuathArray([
    Gf.Quath(1, 0, 0, 0), Gf.Quath(1, 0, 0, 0), Gf.Quath(1, 0, 0, 0), Gf.Quath(1, 0, 0, 0)
]))
```

## Prototype Definition

```python
proto = UsdGeom.Xform.Define(stage, "/Scene/Prototypes/A")
mesh = UsdGeom.Mesh.Define(stage, "/Scene/Prototypes/A/Shape")
mesh.GetPointsAttr().Set(Vt.Vec3fArray([
    (-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5), (-0.5, 0, 0.5),
    (-0.5, 1, -0.5), (0.5, 1, -0.5), (0.5, 1, 0.5), (-0.5, 1, 0.5)
]))
mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray([4, 4, 4, 4, 4, 4]))
mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray([
    0, 1, 2, 3,  4, 5, 6, 7,  0, 1, 5, 4,  2, 3, 7, 6,  0, 3, 7, 4,  1, 2, 6, 5
]))
```

## Collection

```python
scene_prim = stage.GetPrimAtPath("/Scene")
collection = Usd.CollectionAPI.Apply(scene_prim, "myCollection")
collection.GetIncludesRel().AddTarget("/Scene/Instances")
collection.GetIncludesRel().AddTarget("/Scene/Prototypes/A")
```

## Default Prim

```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())
```
