# USD Composition Reference

## Sublayers

Sublayers merge multiple USD files. List stronger opinions first.

```python
from pxr import Usd

stage = Usd.Stage.CreateNew("shot.usda")
stage.GetRootLayer().subLayerPaths.append("./assets.usda")
```

## References

References bring a prim subtree from another file into your scene.

```python
chair = stage.DefinePrim("/Shot/Chair", "Xform")
chair.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
```

## Default Prim

Set a default prim so others can reference your file without specifying a path.

```python
stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
```

## Variant Sets

Create switchable variations on a prim.

```python
prim = stage.DefinePrim("/Asset", "Xform")
vset = prim.GetVariantSets().AddVariantSet("version")
vset.AddVariant("low")
vset.AddVariant("high")

vset.SetVariantSelection("low")
with vset.GetVariantEditContext():
    stage.DefinePrim("/Asset/Geo", "Xform")
```

## Transform Operations

Add translate, rotate, scale to position prims.

```python
from pxr import UsdGeom, Gf

xform = UsdGeom.Xformable(prim)
xform.AddTranslateOp().Set(Gf.Vec3d(1.0, 2.0, 3.0))
xform.AddRotateXYZOp().Set(Gf.Vec3f(0, 90, 0))
xform.AddScaleOp().Set(Gf.Vec3f(2.0, 2.0, 2.0))
```

## Material Binding

Bind a material to geometry.

```python
from pxr import UsdShade, Sdf

mat = UsdShade.Material.Define(stage, "/Looks/Material")
shader = UsdShade.Shader.Define(stage, "/Looks/Material/Shader")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

UsdShade.MaterialBindingAPI(mesh_prim).Bind(mat)
```

## Save Stage

```python
stage.GetRootLayer().Save()
```
