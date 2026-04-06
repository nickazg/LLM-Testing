# ... define all prims ...

## Complete Pattern: Create Stage with Default Prim

```python
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf

stage = Usd.Stage.CreateNew("file.usda")
stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
stage.GetRootLayer().Save()
```

## Sublayers (add content from another file)

```python
stage.GetRootLayer().subLayerPaths.append("./assets.usda")
```

## References with Transform

```python
chair = stage.DefinePrim("/Shot/Set/ChairA", "Xform")
chair.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
UsdGeom.Xformable(chair).AddTranslateOp().Set(Gf.Vec3d(-2.0, 0.0, 0.0))
```

## Variant Sets (with content inside each variant)

```python
vset = prim.GetVariantSets().AddVariantSet("modelVariant")
vset.AddVariant("simple")
vset.AddVariant("detailed")

vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    # Define prims that exist inside this variant
    geo = stage.DefinePrim("/Assets/Chair/Geo", "Mesh")
    # set mesh attrs...

vset.SetVariantSelection("detailed")
with vset.GetVariantEditContext():
    geo = stage.DefinePrim("/Assets/Chair/Geo", "Mesh")
    # set mesh attrs...
```

## Cube Mesh

```python
mesh = UsdGeom.Mesh.Define(stage, "/path/Geo")
mesh.CreatePointsAttr([(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1), (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)])
mesh.CreateFaceVertexCountsAttr([4,4,4,4,4,4])
mesh.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
mesh.CreateSubdivisionSchemeAttr("none")
```

## Lights

```python
sun = UsdLux.DistantLight.Define(stage, "/Shot/Lighting/Sun")
sun.CreateIntensityAttr(50000)

dome = UsdLux.DomeLight.Define(stage, "/Shot/Lighting/Sky")
dome.CreateIntensityAttr(500)
```
