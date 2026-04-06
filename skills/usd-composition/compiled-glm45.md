# Night variant: DomeLight

## Imports

```python
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf
```

## Stage Creation & Default Prim

```python
stage = Usd.Stage.CreateNew("file.usda")
stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
stage.GetRootLayer().Save()
```

## Sublayers

```python
stage.GetRootLayer().subLayerPaths.append("./assets.usda")
```

## References with Transform

```python
chair_a = stage.DefinePrim("/Shot/Set/ChairA", "Xform")
chair_a.GetReferences().AddReference("./assets.usda", "/Assets/Chair")

xformable = UsdGeom.Xformable(chair_a)
xformable.AddTranslateOp().Set(Gf.Vec3d(-2.0, 0.0, 0.0))
```

## Variant Sets - Authoring Content in Each Variant

```python
prim = stage.DefinePrim("/Assets/Chair", "Xform")
vset = prim.GetVariantSets().AddVariantSet("modelVariant")
vset.AddVariant("simple")
vset.AddVariant("detailed")

vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    geo = stage.DefinePrim("/Assets/Chair/Geo", "Mesh")
    # configure mesh...

vset.SetVariantSelection("detailed")
with vset.GetVariantEditContext():
    geo = stage.DefinePrim("/Assets/Chair/Geo", "Mesh")
    # configure mesh...
```

## Lighting in Variants

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

## Simple Cube Mesh

```python
mesh = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
mesh.CreatePointsAttr([
    (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5),
    (-0.5,-0.5,0.5), (0.5,-0.5,0.5), (0.5,0.5,0.5), (-0.5,0.5,0.5),
])
mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
mesh.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
mesh.CreateSubdivisionSchemeAttr("none")
```
