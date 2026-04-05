# USD Composition Reference

## Multi-File Composition

### Sublayers
Sublayers merge opinions from multiple files. Stronger layers are listed first.
```python
from pxr import Usd, Sdf

stage = Usd.Stage.CreateNew("shot.usda")
root_layer = stage.GetRootLayer()
# Add sublayer — path relative to this file
root_layer.subLayerPaths.append("./assets.usda")
```

### References
References bring a prim (and its subtree) from another file into your scene.
```python
chair_a = stage.DefinePrim("/Shot/Set/ChairA", "Xform")
chair_a.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
```

### Default Prim
Always set a default prim — it's what gets referenced when no prim path is specified.
```python
stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
```

## Variant Sets

### Creating Variants
```python
from pxr import Usd, UsdGeom

prim = stage.DefinePrim("/Assets/Chair", "Xform")
vset = prim.GetVariantSets().AddVariantSet("modelVariant")
vset.AddVariant("simple")
vset.AddVariant("detailed")

# Author opinions inside a variant
vset.SetVariantSelection("simple")
with vset.GetVariantEditContext():
    geo = stage.DefinePrim("/Assets/Chair/Geo", "Mesh")
    # ... set mesh attributes
```

### Switching Variants at Runtime
```python
vset = prim.GetVariantSets().GetVariantSet("modelVariant")
vset.SetVariantSelection("detailed")
# Stage now shows the "detailed" variant's opinions
```

## Transform Operations (xformOp)

### Setting Translate
```python
from pxr import UsdGeom, Gf

xformable = UsdGeom.Xformable(prim)
translate_op = xformable.AddTranslateOp()
translate_op.Set(Gf.Vec3d(2.0, 0.0, 0.0))
```

### Common Pattern: Translate + Rotate + Scale
```python
xformable = UsdGeom.Xformable(prim)
xformable.AddTranslateOp().Set(Gf.Vec3d(1, 2, 3))
xformable.AddRotateXYZOp().Set(Gf.Vec3f(0, 45, 0))
xformable.AddScaleOp().Set(Gf.Vec3f(1, 1, 1))
```

## Material Binding

```python
from pxr import UsdShade

# Create material
mat = UsdShade.Material.Define(stage, "/World/Looks/MyMaterial")

# Create shader
shader = UsdShade.Shader.Define(stage, "/World/Looks/MyMaterial/PBRShader")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

# Connect shader to material output
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

# Bind material to geometry
UsdShade.MaterialBindingAPI.Apply(mesh_prim)
UsdShade.MaterialBindingAPI(mesh_prim).Bind(mat)
```

## Lighting

```python
from pxr import UsdLux

# Dome light (environment/IBL)
dome = UsdLux.DomeLight.Define(stage, "/Shot/Lighting/Sky")
dome.CreateIntensityAttr(500)

# Distant light (sun)
sun = UsdLux.DistantLight.Define(stage, "/Shot/Lighting/Sun")
sun.CreateIntensityAttr(50000)
sun.CreateAngleAttr(0.53)  # sun angular diameter
```

## Mesh Definition

```python
from pxr import UsdGeom, Gf, Vt

mesh = UsdGeom.Mesh.Define(stage, "/World/Ground")

# Quad ground plane
mesh.CreatePointsAttr([
    (-5, 0, -5), (5, 0, -5), (5, 0, 5), (-5, 0, 5)
])
mesh.CreateFaceVertexCountsAttr([4])
mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
mesh.CreateSubdivisionSchemeAttr("none")

# Cube (8 vertices, 6 quad faces)
points = [
    (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
    (-1,-1,1),  (1,-1,1),  (1,1,1),  (-1,1,1),
]
face_counts = [4, 4, 4, 4, 4, 4]
face_indices = [
    0,1,2,3,  4,5,6,7,  0,1,5,4,
    2,3,7,6,  0,3,7,4,  1,2,6,5,
]
```

## Stage Save Pattern
```python
stage = Usd.Stage.CreateNew("output.usda")
# ... define prims, set attributes ...
stage.GetRootLayer().Save()
```
