# Add child geometry as needed

## Stage Setup

```python
import hou
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

## PointInstancer Pattern

```python
instancer = UsdGeom.PointInstancer.Define(stage, "/Scene/Instances")

instancer.GetPrototypesRel().SetTargets([
    Sdf.Path("/Scene/Prototypes/ProtoA"),
    Sdf.Path("/Scene/Prototypes/ProtoB"),
])

instancer.GetProtoIndicesAttr().Set(Vt.IntArray([0, 1, 0, 1]))

positions = [Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(2, 0, 0), Gf.Vec3f(3, 0, 0)]
instancer.GetPositionsAttr().Set(Vt.Vec3fArray(positions))
```

## Minimal Prototype

```python
proto = UsdGeom.Xform.Define(stage, "/Scene/Prototypes/ProtoA")
```

## Collection API

```python
collection = Usd.CollectionAPI.Apply(parent_prim, "collectionName")
collection.GetIncludesRel().AddTarget("/path/to/prim")
```
