# USD Shot Assembly — Key API Patterns

## Stage & File Setup
```python
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf

stage = Usd.Stage.CreateNew("file.usda")
stage.SetDefaultPrim(stage.GetPrimAtPath("/Root"))
stage.GetRootLayer().subLayerPaths.append("./other.usda")
stage.GetRootLayer().Save()
```

## References
```python
prim = stage.DefinePrim("/Shot/Set/ChairA", "Xform")
prim.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
```

## Variant Sets (IMPORTANT: use GetVariantEditContext)
```python
vset = prim.GetVariantSets().AddVariantSet("myVariant")
vset.AddVariant("optionA")
vset.SetVariantSelection("optionA")
with vset.GetVariantEditContext():
    # Define prims/attrs inside this context manager
    child = stage.DefinePrim("/Parent/Child", "Xform")
```

## Transforms
```python
xformable = UsdGeom.Xformable(prim)
xformable.AddTranslateOp().Set(Gf.Vec3d(-2.0, 0.0, 0.0))
```

## Lighting
```python
sun = UsdLux.DistantLight.Define(stage, "/Shot/Lighting/Sun")
sun.CreateIntensityAttr(50000)

dome = UsdLux.DomeLight.Define(stage, "/Shot/Lighting/Sky")
dome.CreateIntensityAttr(500)
```
