# 4. Set positions (one Vec3f per instance)

## Stage Access

```python
import hou
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

## PointInstancer Workflow

```python
instancer = UsdGeom.PointInstancer.Define(stage, "/Scene/Instances")

instancer.GetPrototypesRel().SetTargets([
    Sdf.Path("/Scene/Prototypes/A"),
    Sdf.Path("/Scene/Prototypes/B"),
])

instancer.GetProtoIndicesAttr().Set(Vt.IntArray([0, 1, 0, 1]))

positions = [Gf.Vec3f(0, 0, 0), Gf.Vec3f(2, 0, 0), Gf.Vec3f(4, 0, 0), Gf.Vec3f(6, 0, 0)]
instancer.GetPositionsAttr().Set(Vt.Vec3fArray(positions))
```

**Optional - Orientations:** `instancer.GetOrientationsAttr().Set(Vt.QuathArray([Gf.Quath(1,0,0,0)] * count))`

## Prototypes

Prototypes are regular prims (Xform, Mesh, etc.) at paths you reference:

```python
UsdGeom.Xform.Define(stage, "/Scene/Prototypes/A")
UsdGeom.Xform.Define(stage, "/Scene/Prototypes/B")
```

## UsdCollectionAPI

```python
scene_prim = stage.GetPrimAtPath("/Scene")
collection = Usd.CollectionAPI.Apply(scene_prim, "collectionName")
collection.GetIncludesRel().AddTarget("/Scene/Instances")
collection.GetIncludesRel().AddTarget("/Scene/Prototypes/A")
```

## Default Prim (Optional)

```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())
```
