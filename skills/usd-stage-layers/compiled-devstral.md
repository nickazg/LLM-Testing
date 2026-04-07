# Get composed attribute value

## Core Concept

Layers stack with **first = strongest**. When layers have conflicting opinions, the stronger (earlier in list) wins.

```python
from pxr import Usd, Sdf, UsdGeom, Gf
```

## Creating Layers

```python
stage = Usd.Stage.CreateNew("base_layer.usda")
stage.GetRootLayer().Save()
```

## Sublayer Composition

```python
stage = Usd.Stage.CreateInMemory()
root_layer = stage.GetRootLayer()

root_layer.subLayerPaths.append("./look.usda")   # strongest
root_layer.subLayerPaths.append("./anim.usda")   # middle  
root_layer.subLayerPaths.append("./base.usda")   # weakest
```

## Authoring in Layers

```python
xform = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(xform.GetPrim())

char = UsdGeom.Xform.Define(stage, "/Scene/Char")
xformable = UsdGeom.Xformable(char.GetPrim())
translate_op = xformable.AddTranslateOp()
translate_op.Set(Gf.Vec3d(0, 0, 0), 1)   # frame 1
translate_op.Set(Gf.Vec3d(5, 0, 0), 24)  # frame 24

mesh = UsdGeom.Mesh.Define(stage, "/Scene/Char/Body")
mesh.CreatePointsAttr([(-1,-1,-1), (1,-1,-1), (1,1,1), (-1,1,1)])
mesh.CreateFaceVertexCountsAttr([4])
mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
```

## Reading Composed Results

```python
stage = Usd.Stage.Open("composed.usda")
prim = stage.GetPrimAtPath("/Scene/Char")

attr = prim.GetAttribute("xformOp:translate")
val = attr.Get(12)  # value at frame 12
```

## Key Points

- `root_layer.subLayerPaths.append()` — add sublayers
- First sublayer = strongest opinion
- `stage.GetRootLayer().Save()` — persist changes
- `stage.SetDefaultPrim(prim)` — set default prim
