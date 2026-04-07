# First = strongest, last = weakest

## Create and Save Layers

```python
from pxr import Usd, Sdf, UsdGeom, Gf

stage = Usd.Stage.CreateNew("layer.usda")
stage.GetRootLayer().Save()
```

## Sublayer Composition (Order Matters!)

**Stronger layers come FIRST in subLayerPaths:**

```python
stage = Usd.Stage.CreateInMemory()
root_layer = stage.GetRootLayer()

root_layer.subLayerPaths.append("./anim.usda")  # strongest - wins conflicts
root_layer.subLayerPaths.append("./base.usda") # weakest
```

**Key rule:** When layers define the same attribute, the strongest (first) layer's opinion wins. Time samples in a stronger layer override static values in weaker layers.

## Set Default Prim

```python
prim = stage.DefinePrim("/Scene")
stage.SetDefaultPrim(prim)
```

## Author Time-Sampled Transforms

```python
xform = UsdGeom.Xform.Define(stage, "/Object")
xformable = UsdGeom.Xformable(xform.GetPrim())
op = xformable.AddTranslateOp()

op.Set(Gf.Vec3d(0, 0, 0), 1)   # frame 1
op.Set(Gf.Vec3d(5, 0, 0), 24)  # frame 24
```

## Read Composed Values

```python
stage = Usd.Stage.Open("composed.usda")
prim = stage.GetPrimAtPath("/Object")
attr = prim.GetAttribute("xformOp:translate")
val = attr.Get(12)  # value at frame 12
```
