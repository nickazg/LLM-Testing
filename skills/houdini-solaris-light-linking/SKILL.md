# Solaris USD Light Linking & Filtering via Python Script LOP

## Getting the Stage

**CRITICAL:** In a Python Script LOP, always get the stage from the node context:

```python
import hou
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

Do NOT use `Usd.Stage.CreateNew()` — that creates a disconnected stage.

## Light Types

### Distant Light (Directional)

```python
key = UsdLux.DistantLight.Define(stage, "/Scene/Lighting/KeyLight")
key.GetIntensityAttr().Set(50000)
key.GetAngleAttr().Set(1.0)
```

### Dome Light (Environment/IBL)

```python
dome = UsdLux.DomeLight.Define(stage, "/Scene/Lighting/FillLight")
dome.GetIntensityAttr().Set(500)
```

## Light Transforms

Aim lights using xformOps on the light prim:

```python
xf = UsdGeom.Xformable(key.GetPrim())
xf.AddRotateXYZOp().Set(Gf.Vec3f(-45.0, 30.0, 0.0))
```

## Light Filters

Light filters are child prims under the light. For a barn door filter:

```python
barndoor = stage.DefinePrim("/Scene/Lighting/KeyLight/BarnDoor")
barndoor.CreateAttribute("barndoor:top", Sdf.ValueTypeNames.Float).Set(0.2)
barndoor.CreateAttribute("barndoor:bottom", Sdf.ValueTypeNames.Float).Set(-0.1)
barndoor.CreateAttribute("barndoor:left", Sdf.ValueTypeNames.Float).Set(-0.3)
barndoor.CreateAttribute("barndoor:right", Sdf.ValueTypeNames.Float).Set(0.3)
```

Light filters are defined as generic prims (children of the light) with custom attributes for their parameters.

## UsdGeom Purpose

Controls visibility in different render passes:

```python
imageable = UsdGeom.Imageable(prim)
imageable.GetPurposeAttr().Set(UsdGeom.Tokens.render)   # visible in render only
# Other values: UsdGeom.Tokens.proxy, UsdGeom.Tokens.guide
```

## Light Linking via UsdCollectionAPI

Light linking controls which geometry a light illuminates. Apply a collection named `"lightLink"` to the light prim:

### Include Specific Geometry

```python
collection = Usd.CollectionAPI.Apply(key_light_prim, "lightLink")
collection.GetIncludesRel().AddTarget("/Scene/Hero")
```

### Exclude Geometry

```python
collection.GetExcludesRel().AddTarget("/Scene/Environment")
```

### Multiple Lights with Different Linking

Each light can have its own `lightLink` collection:

```python
# KeyLight — illuminates Hero, excludes Environment
key_coll = Usd.CollectionAPI.Apply(key_light_prim, "lightLink")
key_coll.GetIncludesRel().AddTarget("/Scene/Hero")
key_coll.GetExcludesRel().AddTarget("/Scene/Environment")

# RimLight — illuminates only Hero/Body
rim_coll = Usd.CollectionAPI.Apply(rim_light_prim, "lightLink")
rim_coll.GetIncludesRel().AddTarget("/Scene/Hero/Body")
```

## Geometry Setup

### Mesh Cube

```python
body = UsdGeom.Mesh.Define(stage, "/Scene/Hero/Body")
body.GetPointsAttr().Set(Vt.Vec3fArray([
    (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5),
    (-0.5,-0.5,0.5),  (0.5,-0.5,0.5),  (0.5,0.5,0.5),  (-0.5,0.5,0.5),
]))
body.GetFaceVertexCountsAttr().Set(Vt.IntArray([4, 4, 4, 4, 4, 4]))
body.GetFaceVertexIndicesAttr().Set(Vt.IntArray([
    0,1,2,3,  4,5,6,7,  0,1,5,4,  2,3,7,6,  0,3,7,4,  1,2,6,5,
]))
```

### Mesh Quad (Ground)

```python
ground = UsdGeom.Mesh.Define(stage, "/Scene/Environment/Ground")
ground.GetPointsAttr().Set(Vt.Vec3fArray([
    (-5,0,-5), (5,0,-5), (5,0,5), (-5,0,5)
]))
ground.GetFaceVertexCountsAttr().Set(Vt.IntArray([4]))
ground.GetFaceVertexIndicesAttr().Set(Vt.IntArray([0, 1, 2, 3]))
```

## Default Prim

```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())
```
