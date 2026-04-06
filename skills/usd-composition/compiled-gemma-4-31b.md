# Dome light (sky)

## Sublayers

```python
from pxr import Usd

stage = Usd.Stage.CreateNew("shot.usda")
stage.GetRootLayer().subLayerPaths.append("./assets.usda")
```

## References

```python
chair = stage.DefinePrim("/Shot/Set/ChairA", "Xform")
chair.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
```

## Default Prim

```python
stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
```

## Variant Sets

```python
prim = stage.DefinePrim("/Assets/Chair", "Xform")
vset = prim.GetVariantSets().AddVariantSet("modelVariant")
vset.AddVariant("simple")
vset.AddVariant("detailed")

vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    stage.DefinePrim("/Assets/Chair/Geo", "Mesh")
```

## Transform Operations

```python
from pxr import UsdGeom, Gf

xform = UsdGeom.Xformable(prim)
xform.AddTranslateOp().Set(Gf.Vec3d(-2.0, 0.0, 0.0))
```

## Mesh (Cube)

```python
from pxr import UsdGeom

mesh = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
mesh.CreatePointsAttr([
    (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
    (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)
])
mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
mesh.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
mesh.CreateSubdivisionSchemeAttr("none")
```

## Lighting

```python
from pxr import UsdLux

sun = UsdLux.DistantLight.Define(stage, "/Shot/Lighting/Sun")
sun.CreateIntensityAttr(50000)

dome = UsdLux.DomeLight.Define(stage, "/Shot/Lighting/Sky")
dome.CreateIntensityAttr(500)
```

## Save Stage

```python
stage.GetRootLayer().Save()
```
