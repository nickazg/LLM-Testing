# Author inside "detailed" variant

## Pattern: Create Stage, Set Default Prim, Save

```python
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf

stage = Usd.Stage.CreateNew("assets.usda")
stage.DefinePrim("/Assets", "Xform")
stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
stage.GetRootLayer().Save()
```

## Sublayers

```python
stage = Usd.Stage.CreateNew("shot.usda")
stage.GetRootLayer().subLayerPaths.append("./assets.usda")
```

## References with Translate

```python
chair_a = stage.DefinePrim("/Shot/Set/ChairA", "Xform")
chair_a.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
UsdGeom.Xformable(chair_a).AddTranslateOp().Set(Gf.Vec3d(-2.0, 0.0, 0.0))
```

## Variant Sets — Authoring Content Inside Variants

```python
chair = stage.DefinePrim("/Assets/Chair", "Xform")
vset = chair.GetVariantSets().AddVariantSet("modelVariant")
vset.AddVariant("simple")
vset.AddVariant("detailed")

vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    mesh = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
    mesh.CreatePointsAttr([
        (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
        (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)
    ])
    mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
    mesh.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
    mesh.CreateSubdivisionSchemeAttr("none")

vset.SetVariantSelection("detailed")
with vset.GetVariantEditContext():
    mesh2 = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
    mesh2.CreatePointsAttr([
        (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
        (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)
    ])
    mesh2.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
    mesh2.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
    mesh2.CreateSubdivisionSchemeAttr("none")
```

## Lights Inside Variants

```python
lighting = stage.DefinePrim("/Shot/Lighting", "Xform")
lvset = lighting.GetVariantSets().AddVariantSet("lightingVariant")
lvset.AddVariant("day")
lvset.AddVariant("night")

lvset.SetVariantSelection("day")
with lvset.GetVariantEditContext():
    sun = UsdLux.DistantLight.Define(stage, "/Shot/Lighting/Sun")
    sun.CreateIntensityAttr(50000)

lvset.SetVariantSelection("night")
with lvset.GetVariantEditContext():
    sky = UsdLux.DomeLight.Define(stage, "/Shot/Lighting/Sky")
    sky.CreateIntensityAttr(500)
```
