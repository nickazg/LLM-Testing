# Simple ground plane

## Stage Access

```python
import hou
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

## Create Lights

**Distant Light:**
```python
key = UsdLux.DistantLight.Define(stage, "/Lights/KeyLight")
key.GetIntensityAttr().Set(50000)
```

**Dome Light:**
```python
dome = UsdLux.DomeLight.Define(stage, "/Lights/DomeLight")
dome.GetIntensityAttr().Set(500)
```

## Light Transform

```python
xf = UsdGeom.Xformable(light_prim)
xf.AddRotateXYZOp().Set(Gf.Vec3f(-45.0, 30.0, 0.0))
```

## Light Filter (Barn Door)

Create as child prim under the light:
```python
barndoor = stage.DefinePrim("/Lights/KeyLight/BarnDoor")
barndoor.CreateAttribute("barndoor:top", Sdf.ValueTypeNames.Float).Set(0.2)
barndoor.CreateAttribute("barndoor:bottom", Sdf.ValueTypeNames.Float).Set(-0.1)
barndoor.CreateAttribute("barndoor:left", Sdf.ValueTypeNames.Float).Set(-0.3)
barndoor.CreateAttribute("barndoor:right", Sdf.ValueTypeNames.Float).Set(0.3)
```

## Light Linking

Apply a `"lightLink"` collection to control which geometry a light illuminates:

```python
from pxr import Usd

collection = Usd.CollectionAPI.Apply(light_prim, "lightLink")
collection.GetIncludesRel().AddTarget("/Scene/Hero")

collection.GetExcludesRel().AddTarget("/Scene/Environment")
```

**Multiple lights:**
```python
key_coll = Usd.CollectionAPI.Apply(key_light_prim, "lightLink")
key_coll.GetIncludesRel().AddTarget("/Scene/Hero")

rim_coll = Usd.CollectionAPI.Apply(rim_light_prim, "lightLink")
rim_coll.GetIncludesRel().AddTarget("/Scene/Hero/Body")
```

## Basic Geometry (for testing)

```python
ground = UsdGeom.Mesh.Define(stage, "/Scene/Ground")
ground.GetPointsAttr().Set(Vt.Vec3fArray([(-5,0,-5), (5,0,-5), (5,0,5), (-5,0,5)]))
ground.GetFaceVertexCountsAttr().Set(Vt.IntArray([4]))
ground.GetFaceVertexIndicesAttr().Set(Vt.IntArray([0, 1, 2, 3]))
```

## Default Prim

```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())
```
