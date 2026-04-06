# Author content INSIDE "detailed" variant

## Stage Creation & Default Prim

```python
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf

stage = Usd.Stage.CreateNew("file.usda")
stage.SetDefaultPrim(stage.GetPrimAtPath("/Root"))
stage.GetRootLayer().Save()
```

## Sublayers

```python
stage.GetRootLayer().subLayerPaths.append("./assets.usda")
```

## References with Transform

```python
prim = stage.DefinePrim("/Shot/Set/ChairA", "Xform")
prim.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
UsdGeom.Xformable(prim).AddTranslateOp().Set(Gf.Vec3d(-2.0, 0.0, 0.0))
```

## Variant Sets - Complete Pattern

```python
prim = stage.DefinePrim("/Assets/Chair", "Xform")
vset = prim.GetVariantSets().AddVariantSet("modelVariant")
vset.AddVariant("simple")
vset.AddVariant("detailed")

vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    mesh = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
    # set mesh attrs...

vset.SetVariantSelection("detailed")
with vset.GetVariantEditContext():
    mesh = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
    # set mesh attrs...
```

## Lighting Inside Variants

```python
lighting = stage.DefinePrim("/Shot/Lighting", "Xform")
vset = lighting.GetVariantSets().AddVariantSet("lightingVariant")
vset.AddVariant("day")
vset.AddVariant("night")

vset.SetVariantSelection("day")
with vset.GetVariantEditContext():
    sun = UsdLux.DistantLight.Define(stage, "/Shot/Lighting/Sun")
    sun.CreateIntensityAttr(50000)

vset.SetVariantSelection("night")
with vset.GetVariantEditContext():
    sky = UsdLux.DomeLight.Define(stage, "/Shot/Lighting/Sky")
    sky.CreateIntensityAttr(500)
```

## Cube Mesh (8 vertices, 6 faces)

```python
mesh = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
mesh.CreatePointsAttr([
    (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
    (-1,-1,1),  (1,-1,1),  (1,1,1),  (-1,1,1)
])
mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
mesh.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
mesh.CreateSubdivisionSchemeAttr("none")
```
