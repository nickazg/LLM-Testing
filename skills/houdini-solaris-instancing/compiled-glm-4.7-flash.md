# Add child geometry as needed

## Stage Setup

```python
import hou
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

## PointInstancer - Core Pattern

```python
instancer = UsdGeom.PointInstancer.Define(stage, "/Scene/Instances")

instancer.GetPrototypesRel().SetTargets([
    Sdf.Path("/Scene/Prototypes/A"),
    Sdf.Path("/Scene/Prototypes/B"),
])

instancer.GetProtoIndicesAttr().Set(Vt.IntArray([0, 1, 0, 1]))

positions = [Gf.Vec3f(0,0,0), Gf.Vec3f(2,0,0), Gf.Vec3f(4,0,0), Gf.Vec3f(6,0,0)]
instancer.GetPositionsAttr().Set(Vt.Vec3fArray(positions))
```

## Prototypes

Prototypes are prims the instancer references. Define them before the instancer:
```python
proto = UsdGeom.Xform.Define(stage, "/Scene/Prototypes/A")
```

## UsdCollectionAPI (Optional)

```python
collection = Usd.CollectionAPI.Apply(parent_prim, "myCollection")
collection.GetIncludesRel().AddTarget("/path/to/include")
```
