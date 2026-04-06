# Author content inside each variant

## Stage Creation & Save

```python
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf

stage = Usd.Stage.CreateNew("file.usda")
stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
stage.GetRootLayer().Save()
```

## Sublayers

```python
stage.GetRootLayer().subLayerPaths.append("./assets.usda")
```

## References

```python
prim = stage.DefinePrim("/Shot/Set/ChairA", "Xform")
prim.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
```

## Variant Sets

```python
vset = prim.GetVariantSets().AddVariantSet("modelVariant")
vset.AddVariant("simple")
vset.AddVariant("detailed")

vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    geo = stage.DefinePrim("/Assets/Chair/Geo", "Mesh")
```

## Translate Transform

```python
xformable = UsdGeom.Xformable(prim)
xformable.AddTranslateOp().Set(Gf.Vec3d(-2.0, 0.0, 0.0))
```

## Cube Mesh (8 vertices)

```python
mesh = UsdGeom.Mesh.Define(stage, "/Assets/Chair/Geo")
mesh.CreatePointsAttr([
    (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
    (-1,-1,1),  (1,-1,1),  (1,1,1),  (-1,1,1),
])
mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
mesh.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
mesh.CreateSubdivisionSchemeAttr("none")
```

## Lighting

```python
sun = UsdLux.DistantLight.Define(stage, "/Shot/Lighting/Sun")
sun.CreateIntensityAttr(50000)

dome = UsdLux.DomeLight.Define(stage, "/Shot/Lighting/Sky")
dome.CreateIntensityAttr(500)
```
